from __future__ import annotations

import random
from dataclasses import dataclass, field

from .models import (
    CIVILIZATION,
    FIRST_LIFE,
    GUARANTEED_STAGES,
    STAGE_CONFIGS,
    STAGE_ORDER,
    VARIABLES,
    WORLDFORMING,
    CivilizationProfile,
    SpeciesProfile,
    empty_variable_map,
)


@dataclass
class PlanetState:
    rng: random.Random
    seed: int
    stage: str = WORLDFORMING
    turn: int = 0
    stage_turn: int = 0
    stage_goal: int = 0
    year: int = 0
    habitability: int = 36
    life_bar: int = 58
    variables: dict[str, float] = field(default_factory=empty_variable_map)
    entropy: float = 0.0
    ingenuity_age_threshold: int = 20
    current_age: str = "The Silent Cradle"
    world_origin: str = "Stone drifts beneath a quiet sun."
    dominant_species: SpeciesProfile | None = None
    civilization: CivilizationProfile | None = None
    last_civilization_event: str = "No city speaks."
    recent_consequences: list[str] = field(default_factory=list)
    ages_seen: int = 0
    collapse_marks: int = 0
    recoveries: int = 0
    in_crisis: bool = False
    extinction: bool = False
    extinction_text: str = ""

    def __post_init__(self) -> None:
        self.reset_stage_goal()

    def reset_stage_goal(self) -> None:
        config = STAGE_CONFIGS[self.stage]
        self.stage_goal = self.rng.randint(config.min_turns, config.max_turns)

    def stage_index(self) -> int:
        return STAGE_ORDER.index(self.stage)

    def advance_clock(self) -> None:
        self.turn += 1
        self.stage_turn += 1
        low, high = STAGE_CONFIGS[self.stage].year_step
        self.year += self.rng.randint(low, high)

    def set_stage(self, new_stage: str) -> None:
        self.stage = new_stage
        self.stage_turn = 0
        self.reset_stage_goal()

    def threshold_for(self, variable: str) -> int:
        if variable == "Ingenuity":
            return self.ingenuity_age_threshold
        return 20

    def meter_name(self) -> str:
        return "Habitability" if self.stage == WORLDFORMING else "Life Bar"

    def meter_value(self) -> int:
        return self.habitability if self.stage == WORLDFORMING else self.life_bar

    def meter_label(self) -> str:
        value = self.meter_value()
        if self.stage == WORLDFORMING:
            if value >= 85:
                return "The world is welcoming."
            if value >= 65:
                return "The world can bear life."
            if value >= 45:
                return "The world leans toward mercy."
            if value >= 25:
                return "The world is harsh."
            return "The world resists the seed."
        if value >= 85:
            return "Life is abundant."
        if value >= 65:
            return "Life endures with strength."
        if value >= 45:
            return "Life holds its ground."
        if value >= 25:
            return "Life bends under strain."
        if value > 0:
            return "Life clings by its nails."
        return "Life has fallen silent."

    def meter_bar(self, width: int = 20) -> str:
        filled = max(0, min(width, round(self.meter_value() / 100 * width)))
        return "[" + ("#" * filled) + ("-" * (width - filled)) + "]"

    def apply_variable_changes(self, deltas: dict[str, int | float], factor: float = 1.0) -> None:
        for variable in VARIABLES:
            amount = float(deltas.get(variable, 0.0)) * factor
            self.variables[variable] += amount
            if variable == "Ingenuity":
                cap = max(120.0, float(self.ingenuity_age_threshold + 20))
                self.variables[variable] = max(-30.0, min(cap, self.variables[variable]))
            else:
                self.variables[variable] = max(-30.0, min(30.0, self.variables[variable]))

    def adjust_measure(self, delta: int) -> None:
        if self.stage == WORLDFORMING:
            self.habitability = max(5, min(100, self.habitability + delta))
            return
        self.life_bar = max(0, min(100, self.life_bar + delta))
        if self.stage == FIRST_LIFE and self.life_bar < 8:
            self.life_bar = 8

    def derived_biases(self) -> dict[str, float]:
        values = self.variables
        return {
            "Aquatic Bias": values["Oceans"] * 1.2 + values["Moisture"] * 0.8 + values["Diversity"] * 0.3 - values["Upheaval"] * 0.3,
            "Terrestrial Bias": values["Fertility"] * 1.1 + values["Warmth"] * 0.6 - values["Oceans"] * 0.4 - values["Tempest"] * 0.2,
            "Aerial Bias": values["Tempest"] * 1.0 + values["Warmth"] * 0.5 + values["Ingenuity"] * 0.25 - values["Oceans"] * 0.2,
            "Subterranean Bias": values["Upheaval"] * 1.1 + values["Fertility"] * 0.3 + values["Dominance"] * 0.2 - values["Moisture"] * 0.3,
            "Cooperation": values["Diversity"] * 0.9 + values["Fertility"] * 0.3 - values["Dominance"] * 0.7 - values["Tempest"] * 0.2,
            "Aggression": values["Dominance"] * 0.9 + values["Tempest"] * 0.6 + values["Upheaval"] * 0.5 - values["Moisture"] * 0.2,
            "Adaptability": values["Diversity"] * 0.7 + values["Ingenuity"] * 0.8 + values["Moisture"] * 0.2 - values["Dominance"] * 0.2,
            "Curiosity": values["Ingenuity"] * 1.0 + values["Warmth"] * 0.3 + values["Oceans"] * 0.2 - values["Tempest"] * 0.1,
            "Resilience": values["Upheaval"] * 0.5 + values["Tempest"] * 0.4 + values["Fertility"] * 0.3 + values["Diversity"] * 0.4,
        }

    def environmental_support_score(self) -> float:
        values = self.variables
        warmth_balance = max(0.0, 12.0 - abs(values["Warmth"] - 4.0))
        moisture_balance = max(0.0, 12.0 - abs(values["Moisture"]))
        support = (
            values["Diversity"] * 0.45
            + values["Fertility"] * 0.5
            + warmth_balance * 0.85
            + moisture_balance * 0.85
            + values["Oceans"] * 0.15
        )
        stress = (
            abs(values["Tempest"]) * 0.55
            + abs(values["Upheaval"]) * 0.55
            + max(0.0, values["Dominance"] - values["Diversity"]) * 0.8
        )
        return support - stress

    def worldforming_support_score(self) -> float:
        values = self.variables
        warmth_balance = max(0.0, 10.0 - abs(values["Warmth"] - 3.0))
        moisture_balance = max(0.0, 10.0 - abs(values["Moisture"]))
        oceans_balance = max(0.0, 12.0 - abs(values["Oceans"]))
        support = warmth_balance + moisture_balance + oceans_balance + values["Fertility"] * 0.6
        stress = abs(values["Tempest"]) * 0.65 + abs(values["Upheaval"]) * 0.45
        return support - stress

    def top_variables(self, count: int = 3) -> list[tuple[str, float]]:
        ranked = sorted(self.variables.items(), key=lambda item: abs(item[1]), reverse=True)
        return ranked[:count]

    def lowest_variables(self, count: int = 3) -> list[tuple[str, float]]:
        ranked = sorted(self.variables.items(), key=lambda item: item[1])
        return ranked[:count]

    def visible_species_summary(self) -> str:
        if not self.dominant_species:
            if self.stage == WORLDFORMING:
                return "No creature rules. The cradle is still being made."
            return "No creature holds the world for long."
        return self.dominant_species.summary

    def visible_civilization_summary(self) -> str:
        if not self.civilization:
            return "No city has found its voice."
        return self.civilization.summary

    def record_consequences(self, lines: list[str]) -> None:
        self.recent_consequences = lines[-5:]

    def crisis_active(self) -> bool:
        return self.stage != WORLDFORMING and self.life_bar < 25

    def update_crisis_flag(self) -> bool:
        now = self.crisis_active()
        recovered = self.in_crisis and self.life_bar >= 35
        self.in_crisis = now
        if recovered:
            self.recoveries += 1
        return recovered

    def ensure_early_survival(self) -> None:
        if self.stage in GUARANTEED_STAGES[:2] and self.stage != WORLDFORMING and self.life_bar < 8:
            self.life_bar = 8

    def mark_extinction(self, text: str) -> None:
        self.extinction = True
        self.life_bar = 0
        self.extinction_text = text

    def civilization_pressure(self) -> int:
        if not self.civilization:
            return 0
        stage_bonus = 2 if self.stage in (CIVILIZATION,) else 1
        return stage_bonus + max(0, self.collapse_marks)
