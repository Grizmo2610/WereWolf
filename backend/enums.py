from enum import Enum


class Faction(str, Enum):
    VILLAGE = "village"
    WOLF = "wolf"
    NEUTRAL = "neutral"


class Phase(str, Enum):
    LOBBY = "lobby"
    NIGHT = "night"
    DAY_DISCUSSION = "day_discussion"
    DAY_VOTE = "day_vote"
    ENDED = "ended"


class RoleId(str, Enum):
    VILLAGER = "villager"
    SEER = "seer"
    GUARD = "guard"
    WITCH = "witch"
    HUNTER = "hunter"
    WEREWOLF = "werewolf"


class ActionType(str, Enum):
    GUARD_PROTECT = "guard_protect"
    SEER_CHECK = "seer_check"
    WOLF_ATTACK = "wolf_attack"
    WITCH_SAVE = "witch_save"
    WITCH_POISON = "witch_poison"
    HUNTER_SHOOT = "hunter_shoot"
    VOTE = "vote"
    SKIP_TURN = "skip_turn"


class ActionPriority(int, Enum):
    GUARD = 10
    SEER = 20
    WOLF_ATTACK = 30
    WITCH_SAVE = 40
    WITCH_POISON = 50
    CLEANUP = 100


class ProviderName(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
