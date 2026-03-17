from __future__ import annotations

from .models import HistoryEntry


class HistoryLog:
    def __init__(self) -> None:
        self.entries: list[HistoryEntry] = []

    def add(self, year: int, turn: int, text: str, kind: str) -> None:
        self.entries.append(HistoryEntry(year=year, turn=turn, text=text, kind=kind))

    def recent(self, count: int = 6) -> list[HistoryEntry]:
        return self.entries[-count:]

    def since(self, index: int) -> list[HistoryEntry]:
        return self.entries[index:]

    def __len__(self) -> int:
        return len(self.entries)
