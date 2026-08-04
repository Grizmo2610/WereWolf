import asyncio
import random

from agents.agent import Agent
from agents.key_pool import KeyPool
from agents.speech_logger import SpeechLogger
from agents.turn_scheduler import TurnScheduler
from config.settings import get_settings
from db.database import SessionLocal
from db.models import GameRecord, PlayerRecord
from enums import ActionType, Faction, Phase
from game import Game
from resolver import NightActionSubmission, Resolver
from roles.base import get_role
from scenarios import resolve_scenario

settings = get_settings()

NIGHT_ACTION_ORDER = [
    (ActionType.GUARD_PROTECT, "guard"),
    (ActionType.SEER_CHECK, "seer"),
    (ActionType.WOLF_ATTACK, "werewolf"),
    (ActionType.WITCH_SAVE, "witch"),
]


class Room:
    def __init__(self, room_code: str, game: Game, agents: dict[str, Agent],
                 key_pool: KeyPool, db_game_id: int):
        self.room_code = room_code
        self.game = game
        self.agents = agents
        self.key_pool = key_pool
        self.db_game_id = db_game_id
        self.websockets: list = []
        self.resolver = Resolver(game)
        self.task: asyncio.Task | None = None

    def name_of(self, player_id: str | None) -> str | None:
        if not player_id:
            return None
        player = self.game.get_player(player_id)
        return player.display_name if player else None

    async def broadcast(self, payload: dict) -> None:
        dead = []
        for ws in self.websockets:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            if ws in self.websockets:
                self.websockets.remove(ws)

    async def broadcast_public_line(self, text: str, kind: str = "chat",
                                     player_id: str | None = None,
                                     event: str | None = None) -> None:
        self.game.add_public_log(text)
        for agent in self.agents.values():
            agent.observe_public_line(text)
        payload = {
            "type": kind,
            "text": text,
            "player_id": player_id,
            "player_name": self.name_of(player_id),
        }
        if event:
            payload["event"] = event
        await self.broadcast(payload)

    async def broadcast_event(self, text: str, event: str) -> None:
        """Phát sự kiện nổi bật (bắt đầu đêm, có người chết, ...) lên chat."""
        await self.broadcast_public_line(text, kind="system", event=event)

    async def broadcast_state(self) -> None:
        await self.broadcast({
            "type": "state",
            "phase": self.game.phase.value,
            "round": self.game.round_number,
            "players": [
                {
                    "seat_id": p.seat_id,
                    "alive": p.alive,
                    "display_name": p.display_name,
                }
                for p in self.game.players
            ],
        })


class RoomManager:
    def __init__(self):
        self.rooms: dict[str, Room] = {}

    def create_room(self, scenario_id: str, total_players: int,
                     provider_keys: dict[str, list[str]] | None) -> Room:
        scenario = resolve_scenario(scenario_id, total_players)
        game = Game.new(scenario, total_players)

        if provider_keys:
            providers = provider_keys
        else:
            providers = {
                "gemini": settings.gemini_keys_list,
                "openai": settings.openai_keys_list,
            }
            if settings.ollama_enabled:
                providers["ollama"] = settings.ollama_keys_list
            if settings.qwen_vllm_enabled:
                providers["qwen_vllm"] = settings.qwen_vllm_keys_list

        # loại bỏ provider không có key nào cấu hình để không tạo slot rỗng vô nghĩa
        providers = {name: keys for name, keys in providers.items() if keys}

        key_pool = KeyPool(providers)
        key_pool.probe_and_prune()
        key_pool.assign([p.player_id for p in game.players])

        agents: dict[str, Agent] = {}
        for player in game.players:
            agents[player.player_id] = Agent(
                player_id=player.player_id,
                key_pool=key_pool,
                character_name=player.display_name,
                role_id=player.role_id,
            )
            role_def = get_role(player.role_id)
            agents[player.player_id].private_context = (
                f"Vai trò của bạn là {role_def.display_name} ({player.role_id})."
            )

        session = SessionLocal()
        db_game = GameRecord(
            room_code=game.room_code,
            scenario_id=scenario.scenario_id,
            total_players=total_players,
        )
        session.add(db_game)
        session.commit()
        for player in game.players:
            session.add(PlayerRecord(
                game_id=db_game.id,
                player_id=player.player_id,
                seat_id=player.seat_id,
                role_id=player.role_id,
                is_ai=player.is_ai,
                provider_name=key_pool.get_provider_name(player.player_id),
                personality=agents[player.player_id].personality,
            ))
        session.commit()
        session.close()

        room = Room(game.room_code, game, agents, key_pool, db_game.id)
        self.rooms[game.room_code] = room
        return room

    def get_room(self, room_code: str) -> Room | None:
        return self.rooms.get(room_code)

    def start_game(self, room_code: str) -> None:
        room = self.get_room(room_code)
        if room is None:
            return
        room.game.start()
        room.task = asyncio.create_task(run_game_loop(room))


async def run_game_loop(room: Room) -> None:
    session = SessionLocal()
    logger = SpeechLogger(session, room.db_game_id, room.room_code)
    try:
        # In danh sách nhân vật + role ngay khi ván bắt đầu
        logger.log_game_start(room.game.players)

        while room.game.phase != Phase.ENDED:
            await run_night(room, logger)
            winner = room.game.check_winner()
            if winner:
                await finish_game(room, winner)
                break

            room.game.advance_to_day()
            await room.broadcast_state()
            logger.log_phase(f"☀️  CHUYỂN SANG BAN NGÀY — Ngày {room.game.round_number}")
            await run_day_discussion(room, logger)

            room.game.advance_to_vote()
            await room.broadcast_state()
            logger.log_phase(f"🗳️  BỎ PHIẾU TREO CỔ — Ngày {room.game.round_number}")
            await run_vote(room, logger)
            winner = room.game.check_winner()
            if winner:
                await finish_game(room, winner)
                break

            room.game.advance_to_night()
            await room.broadcast_state()
    except Exception as exc:
        import logging as _logging
        _logging.getLogger("werewolf").exception("Game loop lỗi ở phòng %s: %s", room.room_code, exc)
        await room.broadcast_public_line(f"Lỗi hệ thống: {exc}", kind="system")
    finally:
        session.close()


async def run_night(room: Room, logger: SpeechLogger) -> None:
    game = room.game
    logger.log_phase(f"🌙 CHUYỂN SANG BAN ĐÊM — Đêm {game.round_number}")
    await room.broadcast_event(f"🌙 Đêm {game.round_number} bắt đầu — làng chìm vào bóng tối.", event="night_start")

    # Nhãn hiển thị cho từng action type
    ACTION_LABEL = {
        "guard_protect": "🛡️  BẢO VỆ hành động",
        "seer_check":    "🔮 TIÊN TRI soi",
        "wolf_attack":   "🐺 SÓI vote mục tiêu",
        "witch_save":    "🧪 PHÙ THỦY dùng thuốc cứu",
        "witch_poison":  "☠️  PHÙ THỦY dùng thuốc độc",
        "hunter_shoot":  "🏹 THỢ SĂN bắn",
    }

    submissions: list[NightActionSubmission] = []
    for action_type, role_id in NIGHT_ACTION_ORDER:
        actors = [p for p in game.alive_players() if p.role_id == role_id]
        if not actors:
            continue

        label = ACTION_LABEL.get(action_type.value, f"{role_id.upper()} hành động")
        actor_names = ", ".join(p.display_name for p in actors)
        logger.log_phase(f"{label} ({actor_names})")

        for player in actors:
            agent = room.agents[player.player_id]
            decision = await asyncio.to_thread(agent.decide_night_action, game)
            logger.log_action(player.player_id, player.display_name,
                               room.key_pool.get_provider_name(player.player_id),
                               action_type.value, decision.target_id,
                               room.name_of(decision.target_id), decision.reason)
            submissions.append(NightActionSubmission(
                player_id=player.player_id,
                action_type=action_type,
                target_id=decision.target_id,
                reason=decision.reason,
            ))
    result = room.resolver.resolve_night(submissions)
    died = game.apply_night_result(result)

    if game.pending_hunter_shot:
        await handle_hunter_shot(room, logger)

    if died:
        names = ", ".join(p.display_name for p in died)
        await room.broadcast_event(
            f"💀 Đêm {game.round_number} kết thúc — {names} đã chết.",
            event="player_died"
        )
    else:
        await room.broadcast_event(
            f"🌅 Đêm {game.round_number} kết thúc — không ai thiệt mạng.",
            event="night_end"
        )


async def handle_hunter_shot(room: Room, logger: SpeechLogger) -> None:
    game = room.game
    hunter_id = game.pending_hunter_shot
    agent = room.agents.get(hunter_id)
    hunter = game.get_player(hunter_id)
    if not agent or not hunter:
        game.pending_hunter_shot = None
        return
    logger.log_phase(f"🏹 THỢ SĂN bắn ({hunter.display_name})")
    decision = await asyncio.to_thread(agent.decide_night_action, game)
    logger.log_action(hunter_id, hunter.display_name, room.key_pool.get_provider_name(hunter_id),
                       ActionType.HUNTER_SHOOT.value, decision.target_id,
                       room.name_of(decision.target_id), decision.reason)
    target = game.apply_hunter_shot(decision.target_id) if decision.target_id else None
    if target:
        await room.broadcast_event(
            f"🏹 Thợ Săn bắn theo {target.display_name}!",
            event="player_died"
        )


async def run_day_discussion(room: Room, logger: SpeechLogger) -> None:
    game = room.game
    seat_order = {p.player_id: p.seat_id for p in game.players}
    scheduler = TurnScheduler(room.key_pool.key_groups(), seat_order)

    loop = asyncio.get_event_loop()
    deadline = loop.time() + settings.discussion_timeout_seconds
    min_turn = settings.min_turn_seconds
    is_first_turn = True  # người đầu tiên bắt buộc phải nói

    while loop.time() < deadline and scheduler.turns_used < settings.max_turns_per_day:
        alive_ids = {p.player_id for p in game.alive_players()}
        if not alive_ids:
            break
        player_id = scheduler.next_agent(alive_ids)
        if player_id is None:
            break

        turn_start = loop.time()

        agent = room.agents[player_id]
        player = game.get_player(player_id)
        provider_name = room.key_pool.get_provider_name(player_id)
        think_result = await asyncio.to_thread(agent.think, game)

        # Người đầu tiên lên tiếng trong ngày bắt buộc phải nói
        if is_first_turn:
            think_result.will_speak = True
            is_first_turn = False

        logger.log_think(player_id, player.display_name, provider_name, think_result.will_speak,
                          think_result.reasoning, think_result.intent)
        if think_result.will_speak:
            text = await asyncio.to_thread(agent.speak, think_result)
            logger.log_speak(player_id, player.display_name, provider_name, text)
            if text:
                await room.broadcast_public_line(text, kind="chat", player_id=player_id)

        # Đảm bảo mỗi lượt tối thiểu min_turn_seconds
        elapsed_turn = loop.time() - turn_start
        delay = settings.turn_delay_seconds.get(provider_name, 2)
        remaining = max(min_turn - elapsed_turn, delay)
        await asyncio.sleep(remaining)


async def run_vote(room: Room, logger: SpeechLogger) -> None:
    game = room.game
    await room.broadcast_event("🗳️ Bắt đầu bỏ phiếu — ai sẽ bị treo cổ hôm nay?", event="vote_start")

    votes: dict[str, str] = {}
    for player in game.alive_players():
        agent = room.agents[player.player_id]
        decision = await asyncio.to_thread(agent.decide_vote, game)
        logger.log_action(player.player_id, player.display_name,
                           room.key_pool.get_provider_name(player.player_id),
                           ActionType.VOTE.value, decision.target_id,
                           room.name_of(decision.target_id), decision.reason)
        if decision.target_id:
            votes[player.player_id] = decision.target_id
    target_id = room.resolver.resolve_vote(votes)
    victim = game.apply_vote_result(target_id)

    if game.pending_hunter_shot:
        await handle_hunter_shot(room, logger)

    if victim:
        await room.broadcast_event(
            f"⚖️ {victim.display_name} bị làng treo cổ!",
            event="player_executed"
        )
    else:
        await room.broadcast_event("⚖️ Không ai bị treo cổ hôm nay — bỏ phiếu hòa.", event="vote_end")


async def finish_game(room: Room, winner: Faction) -> None:
    room.game.end(winner)
    label = "Dân làng" if winner == Faction.VILLAGE else "Sói"
    await room.broadcast_event(f"🏆 Trò chơi kết thúc — Phe {label} chiến thắng!", event="game_end")
    await room.broadcast_state()

    session = SessionLocal()
    db_game = session.get(GameRecord, room.db_game_id)
    if db_game:
        db_game.started_at = room.game.started_at
        db_game.ended_at = room.game.ended_at
        db_game.winner_faction = winner.value
        session.commit()
    session.close()