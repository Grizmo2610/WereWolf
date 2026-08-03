import uuid
from dataclasses import dataclass, field

from enums import Faction


@dataclass
class Player:
    player_id: str
    seat_id: int
    role_id: str
    faction: Faction
    is_ai: bool
    display_name: str
    alive: bool = True
    died_round: int | None = None
    death_cause: str | None = None
    protected_last_round: bool = False
    poison_immune_target: bool = False

    @staticmethod
    def new(seat_id: int, role_id: str, faction: Faction, is_ai: bool, display_name: str) -> "Player":
        return Player(
            player_id=str(uuid.uuid4()),
            seat_id=seat_id,
            role_id=role_id,
            faction=faction,
            is_ai=is_ai,
            display_name=display_name,
        )

    def kill(self, round_number: int, cause: str) -> None:
        if not self.alive:
            return
        self.alive = False
        self.died_round = round_number
        self.death_cause = cause
