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
    
    # Villager faction
    APPRENTICE_SEER = "apprentice_seer"
    MYSTIC_SEER = "mystic_seer"
    CLAIRVOYANT = "clairvoyant"
    DETECTIVE = "detective"
    GHOST = "ghost"
    PRIEST = "priest"
    HUNTRESS = "huntress"
    PLAGUE_BEARER = "plague_bearer"
    CUPID = "cupid"
    TERRORIST = "terrorist"
    HALFBREED = "halfbreed"
    CURSED = "cursed"
    CLONE = "clone"
    GRANDMOTHER = "grandmother"
    RED_HOOD = "red_hood"
    TWINS = "twins"
    SORCERER = "sorcerer"
    OLD_HAG = "old_hag"
    PRINCE = "prince"
    TOUGH_YOUTH = "tough_youth"
    GAMBLER = "gambler"
    DRUNKARD = "drunkard"

    # Wolf faction
    ALPHA_WOLF = "alpha_wolf"
    WOLF_CUB = "wolf_cub"
    LONE_WOLF = "lone_wolf"
    VEGETARIAN_WOLF = "vegetarian_wolf"
    WOLF_SEER = "wolf_seer"
    MEDIUM = "medium"

    # Neutral faction
    FOOL = "fool"
    SOLO_KILLER = "solo_killer"
    CULT_LEADER = "cult_leader"
    VAMPIRE = "vampire"
    SABOTEUR = "saboteur"


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
