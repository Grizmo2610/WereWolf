import random
import string
import time
from dataclasses import dataclass, field

from enums import ActionType, Faction, Phase
from player import Player
from resolver import NightActionSubmission, Resolver
from roles.base import get_role
from scenarios import Scenario, ScenarioFiller


def generate_room_code() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=6))


@dataclass
class NightState:
    submissions: list[NightActionSubmission] = field(default_factory=list)
    guard_last_target: str | None = None
    witch_save_used: bool = False
    witch_poison_used: bool = False


@dataclass
class Game:
    room_code: str
    scenario: Scenario
    players: list[Player] = field(default_factory=list)
    round_number: int = 0
    phase: Phase = Phase.LOBBY
    started_at: float | None = None
    ended_at: float | None = None
    winner_faction: Faction | None = None
    public_log: list[str] = field(default_factory=list)
    night_state: NightState = field(default_factory=NightState)
    pending_hunter_shot: str | None = None

    @staticmethod
    def new(scenario: Scenario, total_players: int) -> "Game":
        role_ids = ScenarioFiller.fill(scenario, total_players)
        players = []
        for seat_id, role_id in enumerate(role_ids):
            role_def = get_role(role_id)
            players.append(Player.new(
                seat_id=seat_id,
                role_id=role_id,
                faction=role_def.faction,
                is_ai=True,
                display_name=f"Người chơi {seat_id + 1}",
            ))
        return Game(room_code=generate_room_code(), scenario=scenario, players=players)

    def get_player(self, player_id: str) -> Player | None:
        for p in self.players:
            if p.player_id == player_id:
                return p
        return None

    def get_by_seat(self, seat_id: int) -> Player | None:
        for p in self.players:
            if p.seat_id == seat_id:
                return p
        return None

    def alive_players(self) -> list[Player]:
        return [p for p in self.players if p.alive]

    def start(self) -> None:
        self.started_at = time.time()
        self.phase = Phase.NIGHT
        self.round_number = 1

    def check_winner(self) -> Faction | None:
        fn = self.scenario.win_condition_fn
        if fn is None:
            return None
        return fn(self)

    def apply_night_result(self, result) -> list[Player]:
        died: list[Player] = []
        for target_id, cause in result.deaths:
            target = self.get_player(target_id)
            if target and target.alive:
                target.kill(self.round_number, cause)
                died.append(target)
                if target.role_id == "hunter":
                    self.pending_hunter_shot = target.player_id
        if result.guard_target:
            self.night_state.guard_last_target = result.guard_target
        return died

    def apply_hunter_shot(self, target_id: str) -> Player | None:
        target = self.get_player(target_id)
        if target and target.alive:
            target.kill(self.round_number, "hunter_shot")
        self.pending_hunter_shot = None
        return target

    def apply_vote_result(self, target_id: str | None) -> Player | None:
        if not target_id:
            return None
        target = self.get_player(target_id)
        if target and target.alive:
            target.kill(self.round_number, "voted_out")
            if target.role_id == "hunter":
                self.pending_hunter_shot = target.player_id
            return target
        return None

    def add_public_log(self, line: str) -> None:
        self.public_log.append(line)

    def advance_to_day(self) -> None:
        self.phase = Phase.DAY_DISCUSSION

    def advance_to_vote(self) -> None:
        self.phase = Phase.DAY_VOTE

    def advance_to_night(self) -> None:
        self.round_number += 1
        self.phase = Phase.NIGHT
        self.night_state = NightState(guard_last_target=self.night_state.guard_last_target)

    def end(self, winner: Faction) -> None:
        self.phase = Phase.ENDED
        self.winner_faction = winner
        self.ended_at = time.time()
