import random
from dataclasses import dataclass, field
from typing import Callable

from enums import Faction
from roles.base import get_role


@dataclass
class Scenario:
    scenario_id: str
    display_name: str
    min_players: int
    max_players: int
    fixed_roles: list[str]
    fill_pool: list[str] = field(default_factory=lambda: ["villager"])
    win_condition_fn: Callable[["object"], Faction | None] | None = None


def default_win_condition(game) -> Faction | None:
    alive = [p for p in game.players if p.alive]
    wolves = [p for p in alive if p.faction == Faction.WOLF]
    others = [p for p in alive if p.faction != Faction.WOLF]
    if not wolves:
        return Faction.VILLAGE
    if len(wolves) >= len(others):
        return Faction.WOLF
    return None


SCENARIOS: dict[str, Scenario] = {
    "classic_9": Scenario(
        scenario_id="classic_9",
        display_name="Kịch bản thường (9 người)",
        min_players=9,
        max_players=9,
        fixed_roles=["werewolf", "werewolf", "seer", "guard", "witch", "hunter",
                      "villager", "villager", "villager"],
        fill_pool=["villager"],
        win_condition_fn=default_win_condition,
    ),
}


class ScenarioFiller:
    @staticmethod
    def fill(scenario: Scenario, total_players: int) -> list[str]:
        roles = list(scenario.fixed_roles)
        if total_players < len(roles):
            raise ValueError("total_players nhỏ hơn số vai cố định của kịch bản")
        pool_index = 0
        while len(roles) < total_players:
            roles.append(scenario.fill_pool[pool_index % len(scenario.fill_pool)])
            pool_index += 1
        random.shuffle(roles)
        return roles


def resolve_scenario(scenario_id: str, total_players: int) -> Scenario:
    if scenario_id == "random":
        candidates = [s for s in SCENARIOS.values() if s.min_players <= total_players <= s.max_players]
        if not candidates:
            candidates = list(SCENARIOS.values())
        return random.choice(candidates)
    return SCENARIOS[scenario_id]
