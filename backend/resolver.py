from __future__ import annotations

from dataclasses import dataclass

from enums import ActionType, Faction


@dataclass
class NightActionSubmission:
    player_id: str
    action_type: ActionType
    target_id: str | None
    reason: str


@dataclass
class NightResult:
    deaths: list[tuple[str, str]]
    guard_target: str | None
    seer_result: tuple[str, Faction] | None = None


class Resolver:
    def __init__(self, game):
        self.game = game

    def resolve_night(self, submissions: list[NightActionSubmission]) -> NightResult:
        by_type: dict[ActionType, list[NightActionSubmission]] = {}
        for sub in submissions:
            by_type.setdefault(sub.action_type, []).append(sub)

        guard_target = None
        guard_subs = by_type.get(ActionType.GUARD_PROTECT, [])
        if guard_subs:
            guard_target = guard_subs[0].target_id

        seer_result = None
        seer_subs = by_type.get(ActionType.SEER_CHECK, [])
        if seer_subs and seer_subs[0].target_id:
            target = self.game.get_player(seer_subs[0].target_id)
            if target:
                seer_result = (target.player_id, target.faction)

        wolf_target = None
        wolf_subs = by_type.get(ActionType.WOLF_ATTACK, [])
        if wolf_subs:
            counts: dict[str, int] = {}
            for sub in wolf_subs:
                if sub.target_id:
                    counts[sub.target_id] = counts.get(sub.target_id, 0) + 1
            if counts:
                wolf_target = max(counts.items(), key=lambda kv: kv[1])[0]

        witch_save_subs = by_type.get(ActionType.WITCH_SAVE, [])
        witch_saved = bool(witch_save_subs and witch_save_subs[0].target_id == wolf_target)

        deaths: list[tuple[str, str]] = []
        if wolf_target and wolf_target != guard_target and not witch_saved:
            deaths.append((wolf_target, "wolf_attack"))

        witch_poison_subs = by_type.get(ActionType.WITCH_POISON, [])
        if witch_poison_subs and witch_poison_subs[0].target_id:
            deaths.append((witch_poison_subs[0].target_id, "witch_poison"))

        return NightResult(deaths=deaths, guard_target=guard_target, seer_result=seer_result)

    def resolve_vote(self, votes: dict[str, str]) -> str | None:
        if not votes:
            return None
        counts: dict[str, int] = {}
        for target in votes.values():
            counts[target] = counts.get(target, 0) + 1
        top = max(counts.values())
        top_targets = [pid for pid, c in counts.items() if c == top]
        if len(top_targets) != 1:
            return None
        return top_targets[0]
