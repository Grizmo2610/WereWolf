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
    custom_rules: dict | None = None
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

    # --- fairy_tale_11_13 ---
    "fairy_tale_11_13": Scenario(
        scenario_id="fairy_tale_11_13",
        display_name="Làng Truyện Kiều (11-13 người)",
        min_players=11,
        max_players=13,
        fixed_roles=["werewolf", "werewolf", "seer", "guard", "witch", "hunter",
                      "villager", "villager", "villager", "grandmother", "red_hood"],
        fill_pool=["villager"],
        custom_rules={"grandmother_red_hood_side_role": True},
        win_condition_fn=default_win_condition, # TODO
    ),

    # --- mystery_9 --- HARD TO IMPLEMENT
    # "mystery_9": Scenario(
    #     scenario_id="mystery_9",
    #     display_name="Làng Bí Ẩn (9 người)",
    #     min_players=9,
    #     max_players=9,
    #     fixed_roles=["villager", "villager", "villager", "villager", "villager",
    #                   "guard", "witch", "hunter", "sorcerer"],
    #     fill_pool=["villager"],
    #     custom_rules={"phantom_victim": True, "no_wolves": True, "no_seer_roles": True,
    #                   "villager_win_by_declaration": True},
    #     win_condition_fn=None, # TODO
    # ),

    # --- massacre_20 ---
    "massacre_20": Scenario(
        scenario_id="massacre_20",
        display_name="Làng Thảm Sát (20 người)",
        min_players=20,
        max_players=20,
        fixed_roles=["werewolf", "werewolf", "werewolf", "alpha_wolf", "wolf_cub",
                      "lone_wolf", "wolf_seer", "medium", "terrorist", "gambler",
                      "vampire", "cult_leader", "cupid", "seer", "guard", "witch",
                      "hunter", "huntress", "detective", "fool", "saboteur"],
        fill_pool=["villager"],
        custom_rules={"forbid_role_asking": True, "all_power_roles": True},
        win_condition_fn=default_win_condition, # TODO
    ),

    # --- twin_villages_20 ---
    "twin_villages_20": Scenario(
        scenario_id="twin_villages_20",
        display_name="Hai Làng Song Sinh (20 người)",
        min_players=20,
        max_players=20,
        fixed_roles=["werewolf", "werewolf", "seer", "guard", "witch", "hunter",
                      "villager", "villager", "villager", "villager",
                      "werewolf", "werewolf", "seer", "guard", "witch", "hunter",
                      "villager", "villager", "villager", "villager"],
        fill_pool=["villager"],
        custom_rules={"split_villages": True, "max_switches_per_player": 2,
                      "independent_villages": True},
        win_condition_fn=None,
    ),

    # --- chaos_slums_12 ---
    "chaos_slums_12": Scenario(
        scenario_id="chaos_slums_12",
        display_name="Khu Slum Hỗn Loạn (12 người)",
        min_players=12,
        max_players=12,
        fixed_roles=["werewolf", "werewolf", "seer", "guard",
                      "drunkard", "gambler", "detective", "fool",
                      "villager", "villager", "villager", "villager"],
        fill_pool=["villager"],
        custom_rules={"shady_roles_focus": True, "low_trust_theme": True},
        win_condition_fn=default_win_condition,
    ),

    # --- medieval_16 ---
    "medieval_16": Scenario(
        scenario_id="medieval_16",
        display_name="Làng Trung Cổ (16 người)",
        min_players=16,
        max_players=16,
        fixed_roles=["witch", "witch", "witch", "witch", "witch",
                      "guard", "hunter", "priest", "tough_youth", "prince",
                      "cupid", "clone", "grandmother", "red_hood",
                      "villager", "villager"],
        fill_pool=["villager"],
        custom_rules={"witches_as_antagonists": True,
                      "villager_witches_double_potions": True,
                      "no_spiritual_roles": True},
        win_condition_fn=default_win_condition, # TODO
    ),

    # --- full_chaos_20 ---
    "full_chaos_20": Scenario(
        scenario_id="full_chaos_20",
        display_name="Hỗn Loạn Hoàn Toàn (20 người)",
        min_players=20,
        max_players=20,
        fixed_roles=[],
        fill_pool=["villager", "seer", "guard", "witch", "hunter", "apprentice_seer",
                   "mystic_seer", "clairvoyant", "detective", "ghost", "priest",
                   "huntress", "plague_bearer", "cupid", "terrorist", "halfbreed",
                   "cursed", "clone", "grandmother", "red_hood", "twins", "sorcerer",
                   "old_hag", "prince", "tough_youth", "gambler", "drunkard",
                   "alpha_wolf", "wolf_cub", "lone_wolf", "vegetarian_wolf",
                   "wolf_seer", "medium", "fool", "solo_killer", "cult_leader",
                   "vampire", "saboteur"],
        custom_rules={"random_assignment": True, "ignore_faction_ratio": True,
                      "wolf_count_floor": 1, "wolf_count_ceiling": 4},
        win_condition_fn=default_win_condition, # TODO
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
