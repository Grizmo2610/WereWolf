# 02 - Scenarios

Each scenario maps to one `Scenario` instance (`backend/scenarios.py`): `name`, `min_players`/`max_players`, `role_pool`, `fixed_roles`, `custom_rules`, `win_condition_fn`. When the room's player count exceeds the scenario's fixed role count, `ScenarioFiller` (see `00-overview-and-architecture.md`) pads the remainder while preserving the original faction ratio — it never just dumps random roles in without regard to balance.

## Classic — 9 players
Baseline setup: 2 Wolves, Seer, Guard, Witch, Hunter, 3 Villagers.
*Optional suggestion: swap one Villager for a Halfbreed to add early misdirection.*

## Fairy-Tale Village — 11-13 players
Classic setup, plus two randomly-chosen Villager-faction players secretly gain the Grandmother/Red Hood side-roles and recognize each other from night 1.
*Optional suggestion: add Prince or Cupid to fit the fairy-tale theme.*

## Mystery Village — 9 players
No Wolves, no seer-type roles at all. Only Villager, Guard, Witch, Hunter, Sorcerer. Each night the system silently picks a "phantom victim" as if a Wolf existed (still subject to Guard/Witch saves). Villagers win if someone correctly calls out the scenario's true nature (a public declaration) before only 2 players remain.

## Massacre Village — 20 players
Every player has a power role, mostly kill-capable ones (Wolves, Terrorist, Gambler, Vampire, Cult Leader, Cupid...). Players are forbidden from directly asking each other's role in discussion — only the Seer and Hunter are allowed to openly discuss their roles.

## Twin Villages — 20 players
Split randomly into two fully independent villages with zero cross-interaction. Each day, one player may request to switch villages (max 2 requests per player); the receiving village votes to accept or reject. Villagers win if they eliminate all Wolves and outnumber the other village; if all Wolves from one village migrate to the other, the vacated village wins immediately.
*Optional suggestion: deliberately split Twins across the two villages to create a natural incentive to migrate and reunite.*

## Chaos Slums — 12 players
Focused on "shady" roles: Drunkard, Gambler, Detective, Fool, plus a minimal base (Wolves, Seer, Guard).
*Optional suggestions: Old Hag, Saboteur, Lone Wolf fit the low-trust theme well.*

## Medieval Village — 16 players
Wolves are replaced by an equivalent number of Witches (antagonist side) who do **not** know each other. Villager-side Witches get double potions. No spiritual/magic roles at all (Seer, Halfbreed, etc. excluded). Antagonist Witches win the same way Wolves normally do.
*Open design question, proposed (not mandatory) resolution options for "act without knowing each other":*
1. Randomly pick one antagonist Witch per night to act alone.
2. Each antagonist Witch submits an independent target; the system executes whichever target got the most votes among them.
3. Each antagonist Witch acts fully independently, producing multiple victims per night.

## Full Chaos — 20 players
Fully random role assignment, faction ratio ignored.
*Optional suggestion: still enforce a safety floor/ceiling on Wolf count to avoid degenerate games (0 Wolves, or Wolves as a near-majority).*