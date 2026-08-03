from dataclasses import dataclass

from enums import Faction


@dataclass(frozen=True)
class RoleDef:
    role_id: str
    display_name: str
    faction: Faction
    faction_goal: str
    has_night_action: bool
    description: str


ROLE_REGISTRY: dict[str, RoleDef] = {}


def register_role(role: RoleDef) -> RoleDef:
    ROLE_REGISTRY[role.role_id] = role
    return role


def get_role(role_id: str) -> RoleDef:
    return ROLE_REGISTRY[role_id]
