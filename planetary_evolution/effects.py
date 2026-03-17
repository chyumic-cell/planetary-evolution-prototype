from __future__ import annotations

from .models import PendingEffect
from .state import PlanetState


class DelayedEffectQueue:
    def __init__(self) -> None:
        self._queue: list[PendingEffect] = []

    def schedule(self, effect: PendingEffect) -> None:
        self._queue.append(effect)

    def extend(self, effects: list[PendingEffect]) -> None:
        self._queue.extend(effects)

    def resolve_due(self, state: PlanetState) -> list[str]:
        due = [effect for effect in self._queue if effect.due_turn <= state.turn]
        self._queue = [effect for effect in self._queue if effect.due_turn > state.turn]
        lines: list[str] = []
        for effect in due:
            state.apply_variable_changes(effect.variable_deltas)
            state.adjust_measure(effect.life_delta)
            lines.append(effect.text)
        return lines

    def pending_count(self) -> int:
        return len(self._queue)
