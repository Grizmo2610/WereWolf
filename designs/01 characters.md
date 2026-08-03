# 01 - Characters (Roles)

Three factions: Villager, Wolf, Neutral. Each role below maps to one `Role` subclass under `backend/roles/` (see `00-overview-and-architecture.md` for file layout). Vietnamese role names are kept alongside English for reference since in-game text stays Vietnamese (see `03-agent-system.md` §1 for the language rule).

## Villager faction (`backend/roles/villagers.py`)

| Role | Vietnamese | Description |
|---|---|---|
| Villager | Dân thường | No special power; discussion + vote only. |
| Seer | Tiên Tri | Each night, pick 1 player, learn their faction. |
| Apprentice Seer | Tiên Tri Tập Sự | Dormant until the real Seer dies, then inherits the Seer's ability. |
| Mystic Seer | Tiên Tri Bí Ẩn | Stronger Seer: learns the exact role, not just faction. |
| Clairvoyant | Ngoại Cảm | Each night, pick 2 players, learn whether they share a faction (not which one). |
| Detective | Thám Tử | One-time use: learns whether the chosen target (or nearest living neighbor) is a Wolf. |
| Ghost | Hồn Ma | Dies on night 1; can hear dead players talk; limited to exactly 1 word per day. |
| Guard | Bảo Vệ | Each night, protect 1 player from wolf attack. Can't repeat the same target two nights in a row. |
| Priest | Mục Sư | One-time protection making a target fully immune to wolf attack (other death causes still apply). |
| Witch | Phù Thủy | One save potion + one poison potion, each usable once per game. |
| Hunter | Thợ Săn | Marks a target each night; if the Hunter dies, the marked target dies too. |
| Huntress | Nữ Thợ Săn | One-time active kill, usable at any point during a night. |
| Plague Bearer | Người Bị Bệnh | If killed by wolves, the wolves are "infected" and skip the next night's kill. |
| Cupid | Cupid | Night 1 only: links two players as lovers — one's death kills the other, regardless of faction. |
| Terrorist | Khủng Bố | On death, both physical seat-neighbors die too. |
| Halfbreed | Con Lai | True Villager, but the Seer sees them as a Wolf (misinformation). |
| Cursed | Kẻ Bị Nguyền | Ordinary Villager; if bitten by wolves, turns into a Wolf instead of dying. |
| Clone | Nhân Bản | Night 1: picks a target; if that target dies, inherits their role. |
| Grandmother | Bà Ngoại | Ordinary Villager, paired with Red Hood. |
| Red Hood | Khăn Đỏ | After Grandmother dies, learns one Wolf's identity per night for the rest of the game. |
| Twins (x2) | Song Sinh | Recognize each other from night 1; can win alone if they're the last surviving pair. |
| Sorcerer | Pháp Sư | Each night, silences one player for the next day (voting still allowed). |
| Old Hag | Mụ Già | Each night, forces one player to sit out the next day (no talk, no vote). |
| Prince | Hoàng Tử | Immune to the first lynch vote against them — revealed publicly instead of dying. |
| Tough Youth | Thanh Niên Cứng | If bitten by wolves, dies one night later instead of immediately. |
| Gambler | Con Bạc | Each night (except night 1), targets a random player: if Wolf, they die; if not, the Gambler dies. |
| Drunkard | Bợm Nhậu | Ordinary Villager who, from night 2 on, has a random chance to "sober up" and receive a new random role. |

## Wolf faction (`backend/roles/wolves.py`)

| Role | Vietnamese | Description |
|---|---|---|
| Werewolf | Sói | The pack wakes together and agrees on one kill target per night. |
| Alpha Wolf | Sói Đầu Đàn | Once per game, converts the target into a Wolf instead of killing them; nullified if the target was protected. |
| Wolf Cub | Sói Con | On death, the next day's lynch vote allows eliminating 2 players instead of 1 (a Villager-side compensating buff). |
| Lone Wolf | Sói Cô Độc | Acts like a normal Wolf but has a separate personal win condition: being the last Wolf alive. |
| Vegetarian Wolf | Sói Ăn Chay | Doesn't participate in kills; still wins with the Wolf faction. |
| Wolf Seer | Sói Tiên Tri | A Wolf with the Seer's faction-reveal ability. |
| Medium | Bà Đồng | Doesn't wake with the pack; secretly tracks the Seer — becomes Wolf Seer if the real Seer dies. |

## Neutral faction (`backend/roles/neutral.py`)

| Role | Vietnamese | Description |
|---|---|---|
| Fool | Kẻ Chán Đời | Wins alone if lynched by vote (only that death cause counts). |
| Solo Killer | Sát Nhân Đơn Độc | Kills one player per night (not a Wolf); wins as the sole survivor. |
| Cult Leader | Chủ Giáo Phái | Each night recruits one player into the cult; wins when every living player is a member. |
| Vampire | Ma Cà Rồng | Drains one player per night — the victim's death is only revealed after the following day's meeting ends; can still be saved. |
| Saboteur | Kẻ Phá Rối | One-time use: swaps the roles of two random players. |

## Notes on implementation

- `Role` metadata (`faction`, `acts_at_night`, `priority`, `max_uses`, `first_night_only`) plus `resolve()`/`on_death()` behavior follows the base contract already defined in `roles/base.py`.
- Per-player mutable state (potions left, tracked target, marked revenge target) lives on `Player.role_state`, never on the `Role` class itself, since a class can be shared by multiple players (e.g. multiple Wolves).
- Wolf-faction roles are always resolved as a block before any other faction at night — see `03-agent-system.md` §3 for the scheduler-level rule.