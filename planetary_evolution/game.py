from __future__ import annotations

import random

from .decisions import DecisionGenerator
from .effects import DelayedEffectQueue
from .history import HistoryLog
from .models import WORLDFORMING
from .narrative import civilization_sign, describe_outcome, final_epitaph, format_year, world_signs
from .state import PlanetState
from .systems import AgeSystem, CivilizationSystem, EntropySystem, SpeciesSystem, StageManager


class GameLoop:
    def __init__(self, seed: int | None = None, auto: bool = False) -> None:
        self.seed = seed if seed is not None else random.SystemRandom().randint(1, 999_999_999)
        self.rng = random.Random(self.seed)
        self.auto = auto
        self.state = PlanetState(rng=self.rng, seed=self.seed)
        self.history = HistoryLog()
        self.history.add(0, 0, "Stone drifts beneath a quiet sun.", "stage")
        self.species_system = SpeciesSystem(self.rng)
        self.age_system = AgeSystem(self.rng, self.species_system)
        self.civilization_system = CivilizationSystem(self.rng)
        self.entropy_system = EntropySystem(self.rng)
        self.stage_manager = StageManager(self.rng, self.species_system)
        self.delayed_effects = DelayedEffectQueue()
        self.decision_generator = DecisionGenerator(self.rng)

    def run(self) -> int:
        while not self.state.extinction:
            self._play_turn()
        self._display_end()
        return self.state.turn

    def _play_turn(self) -> None:
        self.state.advance_clock()
        self.entropy_system.advance(self.state)
        choices = self.decision_generator.generate_choices(self.state)
        self._display_turn(choices)
        selection = self._choose_option(choices)
        history_start = len(self.history)
        consequence_lines, immediate_delta = self._apply_choice(selection)
        consequence_lines.extend(self.delayed_effects.resolve_due(self.state))
        consequence_lines.extend(self.civilization_system.process(self.state, self.history))
        consequence_lines.extend(self.entropy_system.apply_background_instability(self.state))
        drift = self.entropy_system.apply_measure_drift(self.state)
        consequence_lines.append(describe_outcome(selection.category, immediate_delta + drift))
        consequence_lines.extend(self.age_system.process(self.state, self.history))
        consequence_lines.extend(self.stage_manager.process(self.state, self.history))
        if self.state.update_crisis_flag():
            self.history.add(self.state.year, self.state.turn, "Life recovers from the brink.", "recovery")
            consequence_lines.append("Life gathers itself and refuses the grave.")
        self.state.ensure_early_survival()
        if self.state.stage != WORLDFORMING and self.state.life_bar <= 0:
            self.state.mark_extinction(final_epitaph(self.state))
        new_entries = self.history.since(history_start)
        self.state.record_consequences(consequence_lines)
        self._display_resolution(consequence_lines, new_entries)

    def _apply_choice(self, option) -> tuple[list[str], int]:
        factor = self.entropy_system.decision_factor(self.state, option.category)
        self.state.apply_variable_changes(option.immediate_effects, factor)
        immediate_delta = int(round(option.immediate_life_delta * factor))
        self.state.adjust_measure(immediate_delta)
        self.delayed_effects.extend(list(option.pending_effects))
        lines = [f"{option.title} is chosen."]
        if option.category == "stabilizing":
            lines.append("Order is invited in. The cost remains.")
        elif option.category == "destabilizing":
            lines.append("Power is taken through upheaval.")
        else:
            lines.append("A gift and a wound arrive together.")
        return lines, immediate_delta

    def _display_turn(self, choices) -> None:
        print()
        print("=" * 72)
        print(f"Year: {format_year(self.state.year)}")
        print(f"Stage: {self.state.stage}")
        print(f"Age: {self.state.current_age}")
        print(f"{self.state.meter_name()}: {self.state.meter_bar()} {self.state.meter_label()}")
        print("World Signs:")
        for line in world_signs(self.state):
            print(f"- {line}")
        print(f"Dominant Species: {self.state.visible_species_summary()}")
        print(f"Civilization: {civilization_sign(self.state)}")
        print("Choices:")
        for index, option in enumerate(choices, start=1):
            print(f"{index}. {option.title}")
            for text_line in option.text_lines:
                print(f"   {text_line}")
        if self.auto:
            print("Selection: The unseen hand will decide.")

    def _display_resolution(self, consequence_lines, history_entries) -> None:
        print("Consequence:")
        for line in consequence_lines[-6:]:
            print(f"- {line}")
        print("History:")
        if history_entries:
            for entry in history_entries[-6:]:
                print(f"- {format_year(entry.year)}: {entry.text}")
        else:
            print("- The age holds its breath.")

    def _choose_option(self, choices):
        if self.auto:
            return self._auto_choice(choices)
        while True:
            choice = input("Choose one path [1-3]: ").strip()
            if choice in {"1", "2", "3"}:
                return choices[int(choice) - 1]
            print("The world waits for a clear command.")

    def _auto_choice(self, choices):
        if self.state.stage != WORLDFORMING and self.state.life_bar < 25:
            return choices[0]
        if self.state.stage == WORLDFORMING and self.state.habitability < 45:
            return choices[0]
        weights = [4, 2, 3]
        return self.rng.choices(choices, weights=weights, k=1)[0]

    def _display_end(self) -> None:
        print()
        print("=" * 72)
        print(self.state.extinction_text)
        print(f"Final Score: {self.state.turn} turns survived.")
        print(f"Seed: {self.seed}")
