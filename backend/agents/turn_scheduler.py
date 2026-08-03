import random


class TurnScheduler:
    def __init__(self, key_groups: dict[str, list[str]], seat_order: dict[str, int]):
        self.key_groups = {k: sorted(v, key=lambda pid: seat_order[pid]) for k, v in key_groups.items()}
        self.key_ids = list(self.key_groups.keys())
        self.seat_order = seat_order
        self.phase = "guarantee"
        self.spoken_at_least_once: set[str] = set()
        self._group_cursor = {k: 0 for k in self.key_ids}
        self._key_cursor = 0
        self.turns_used = 0

    def _guarantee_done(self) -> bool:
        total_agents = sum(len(v) for v in self.key_groups.values())
        return len(self.spoken_at_least_once) >= total_agents

    def next_agent(self, alive_player_ids: set[str]) -> str | None:
        if self.phase == "guarantee" and self._guarantee_done():
            self.phase = "random"

        if self.phase == "guarantee":
            return self._next_guarantee(alive_player_ids)
        return self._next_random(alive_player_ids)

    def _next_guarantee(self, alive_player_ids: set[str]) -> str | None:
        attempts = 0
        n_keys = len(self.key_ids)
        while attempts < n_keys * 10:
            key_id = self.key_ids[self._key_cursor % n_keys]
            group = self.key_groups[key_id]
            cursor = self._group_cursor[key_id]
            self._key_cursor += 1
            if cursor < len(group):
                candidate = group[cursor]
                self._group_cursor[key_id] += 1
                self.spoken_at_least_once.add(candidate)
                if candidate in alive_player_ids:
                    self.turns_used += 1
                    return candidate
            attempts += 1
        self.phase = "random"
        return self._next_random(alive_player_ids)

    def _next_random(self, alive_player_ids: set[str]) -> str | None:
        if not self.key_ids:
            return None
        key_id = random.choice(self.key_ids)
        group = [pid for pid in self.key_groups[key_id] if pid in alive_player_ids]
        if not group:
            candidates = [pid for pid in alive_player_ids]
            if not candidates:
                return None
            self.turns_used += 1
            return random.choice(candidates)
        self.turns_used += 1
        return random.choice(group)

    def mark_spoken(self, player_id: str) -> None:
        self.spoken_at_least_once.add(player_id)
