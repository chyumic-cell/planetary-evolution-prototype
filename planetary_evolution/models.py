from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


WORLDFORMING = "Worldforming"
FIRST_LIFE = "First Life"
COMPLEX_LIFE = "Complex Life"
GREAT_CREATURES = "Great Creatures"
THINKING_BEASTS = "Thinking Beasts"
CIVILIZATION = "Civilization"
RUIN_RENEWAL = "Ruin or Renewal"

STAGE_ORDER = (
    WORLDFORMING,
    FIRST_LIFE,
    COMPLEX_LIFE,
    GREAT_CREATURES,
    THINKING_BEASTS,
    CIVILIZATION,
    RUIN_RENEWAL,
)

VARIABLES = (
    "Warmth",
    "Moisture",
    "Tempest",
    "Upheaval",
    "Oceans",
    "Fertility",
    "Diversity",
    "Ingenuity",
    "Dominance",
)

GUARANTEED_STAGES = (WORLDFORMING, FIRST_LIFE, COMPLEX_LIFE)


@dataclass(frozen=True)
class StageConfig:
    key: str
    min_turns: int
    max_turns: int
    year_step: tuple[int, int]
    entropy_gain: float


STAGE_CONFIGS = {
    WORLDFORMING: StageConfig(WORLDFORMING, 9, 20, (40_000_000, 140_000_000), 0.35),
    FIRST_LIFE: StageConfig(FIRST_LIFE, 6, 10, (8_000_000, 25_000_000), 0.45),
    COMPLEX_LIFE: StageConfig(COMPLEX_LIFE, 7, 12, (2_000_000, 8_000_000), 0.7),
    GREAT_CREATURES: StageConfig(GREAT_CREATURES, 5, 10, (400_000, 1_800_000), 0.9),
    THINKING_BEASTS: StageConfig(THINKING_BEASTS, 4, 8, (50_000, 300_000), 1.15),
    CIVILIZATION: StageConfig(CIVILIZATION, 5, 9, (2_000, 35_000), 1.5),
    RUIN_RENEWAL: StageConfig(RUIN_RENEWAL, 4, 8, (100, 2_500), 1.9),
}


@dataclass(frozen=True)
class DelayedEffectTemplate:
    min_delay: int
    max_delay: int
    variable_deltas: dict[str, int]
    life_delta: int
    texts: tuple[str, ...]


@dataclass(frozen=True)
class DecisionArchetype:
    key: str
    title: str
    category: str
    compatible_stages: tuple[str, ...]
    effects: dict[str, int]
    life_delta: int
    delayed_templates: tuple[DelayedEffectTemplate, ...]
    tags: tuple[str, ...]
    line_pool_a: tuple[str, ...]
    line_pool_b: tuple[str, ...]
    line_pool_c: tuple[str, ...]


@dataclass
class PendingEffect:
    due_turn: int
    variable_deltas: dict[str, int]
    life_delta: int
    text: str
    source_title: str


@dataclass
class DecisionOption:
    archetype_key: str
    title: str
    category: str
    intensity: int
    text_lines: tuple[str, str, str]
    immediate_effects: dict[str, int]
    immediate_life_delta: int
    pending_effects: list[PendingEffect]
    tags: tuple[str, ...]


@dataclass
class SpeciesProfile:
    name: str
    habitat: str
    traits: tuple[str, ...]
    behaviors: tuple[str, ...]
    lineage: str
    summary: str
    mindful: bool = False


@dataclass
class CivilizationProfile:
    name: str
    origin_species: str
    ethos: str
    focus: str
    summary: str
    stability: int = 50
    legacy: list[str] = field(default_factory=list)
    last_event: str = "Silence watches."


@dataclass
class HistoryEntry:
    year: int
    turn: int
    text: str
    kind: str


def empty_variable_map() -> dict[str, float]:
    return {name: 0.0 for name in VARIABLES}


def non_zero_keys(values: dict[str, int | float]) -> Iterable[str]:
    return (name for name, amount in values.items() if amount)
