from __future__ import annotations

import random

from .history import HistoryLog
from .models import (
    CIVILIZATION,
    COMPLEX_LIFE,
    FIRST_LIFE,
    GREAT_CREATURES,
    RUIN_RENEWAL,
    STAGE_CONFIGS,
    THINKING_BEASTS,
    WORLDFORMING,
    CivilizationProfile,
    SpeciesProfile,
)
from .narrative import build_age_name, world_origin_name
from .state import PlanetState


class SpeciesSystem:
    def __init__(self, rng: random.Random) -> None:
        self.rng = rng
        self.stage_forms = {
            FIRST_LIFE: {
                "aquatic": ["Drifters", "Mats", "Filaments", "Shell Seeds"],
                "amphibious": ["Mud Threads", "Reed Cells", "Brine Crawlers", "Marsh Films"],
                "terrestrial": ["Dust Molds", "Stone Lichen", "Spore Fans", "Root Veils"],
                "aerial": ["Spore Veils", "Sky Motes", "Pollen Clouds", "Mist Threads"],
                "subterranean": ["Vent Worms", "Root Burrowers", "Stone Threads", "Deep Molds"],
            },
            COMPLEX_LIFE: {
                "aquatic": ["Eels", "Shellbacks", "Rayfish", "Mantas"],
                "amphibious": ["Newts", "Reed Stalkers", "Marsh Runners", "Bog Croakers"],
                "terrestrial": ["Sloths", "Grazers", "Lizards", "Beetles"],
                "aerial": ["Gliders", "Moths", "Kites", "Herons"],
                "subterranean": ["Moles", "Ants", "Burrowers", "Rootbacks"],
            },
            GREAT_CREATURES: {
                "aquatic": ["Leviathans", "Crocodiles", "Whales", "Shell Kings"],
                "amphibious": ["Marsh Titans", "Newt Lords", "Fen Striders", "Reed Giants"],
                "terrestrial": ["Sloths", "Lizards", "Mammoths", "Stagbacks"],
                "aerial": ["Raptors", "Moths", "Sky Serpents", "Great Kites"],
                "subterranean": ["Hive Ants", "Stone Moles", "Tunnel Lords", "Burrow Bulls"],
            },
            THINKING_BEASTS: {
                "aquatic": ["Deep Thinkers", "Tide Keepers", "Shell Readers", "Reef Minds"],
                "amphibious": ["Marsh Sages", "Reed Speakers", "Delta Hands", "Mud Scholars"],
                "terrestrial": ["Wise Sloths", "Lizard Clans", "Beetle Houses", "Crown Grazers"],
                "aerial": ["Sky Readers", "Winged Scribes", "Moth Oracles", "Cloud Crows"],
                "subterranean": ["Hive Minds", "Stone Counsels", "Mole Elders", "Deep Ants"],
            },
            CIVILIZATION: {
                "aquatic": ["Tide Keepers", "Shell Readers", "Canal Minds", "Reef Houses"],
                "amphibious": ["Marsh Sages", "Delta Hands", "Fen Houses", "River Speakers"],
                "terrestrial": ["Wise Sloths", "Lizard Clans", "Road Beetles", "Field Houses"],
                "aerial": ["Winged Scribes", "Sky Readers", "Cloud Crows", "Sun Kites"],
                "subterranean": ["Hive Minds", "Deep Ants", "Stone Counsels", "Tunnel Houses"],
            },
            RUIN_RENEWAL: {
                "aquatic": ["Tide Remnants", "Shell Readers", "Salt Houses", "Reef Pilgrims"],
                "amphibious": ["Marsh Keepers", "Fen Pilgrims", "Delta Survivors", "Bog Elders"],
                "terrestrial": ["Last Sloths", "Lizard Remnants", "Beetle Houses", "Dust Walkers"],
                "aerial": ["Ash Wings", "Sky Remnants", "Moth Keepers", "Cloud Pilgrims"],
                "subterranean": ["Last Hive", "Deep Ants", "Stone Keepers", "Tunnel Remnants"],
            },
        }
        self.behavior_adjectives = {
            "Cooperation": ["Choral", "Kinbound", "Common", "Shared"],
            "Aggression": ["Ravenous", "Red Jawed", "Brazen", "Raiding"],
            "Adaptability": ["Wandering", "Shifting", "Quickblood", "Opportunist"],
            "Curiosity": ["Questioning", "Tool Bearing", "Far Seeing", "Thoughtful"],
            "Resilience": ["Stoneback", "Ash Hided", "Enduring", "Hard Shelled"],
        }
        self.habitat_traits = {
            "aquatic": ("finned", "reef-born", "cold-eyed"),
            "amphibious": ("reed-backed", "shore-breeding", "mud-footed"),
            "terrestrial": ("broad-backed", "forest ranging", "slow-blooded"),
            "aerial": ("long-winged", "hollow-boned", "updraft riding"),
            "subterranean": ("burrowing", "stone-sensed", "dark-eyed"),
        }
        self.habitat_places = {
            "aquatic": "They command the water.",
            "amphibious": "They rule the border of land and water.",
            "terrestrial": "They dominate the broad land.",
            "aerial": "They claim the high air and the exposed cliff.",
            "subterranean": "They thrive beneath the world that others see.",
        }

    def generate(self, state: PlanetState, previous: SpeciesProfile | None = None) -> SpeciesProfile:
        biases = state.derived_biases()
        habitat = self._pick_habitat(biases)
        behaviors = self._pick_behaviors(biases)
        stage_key = state.stage if state.stage in self.stage_forms else COMPLEX_LIFE
        noun = self.rng.choice(self.stage_forms[stage_key][habitat])
        adjective = self.rng.choice(self.behavior_adjectives[behaviors[0]])
        if previous and self.rng.random() < 0.45:
            carry = previous.name.split()[0]
            adjective = carry
        name = f"{adjective} {noun}"
        traits = tuple(self.habitat_traits[habitat][:2]) + tuple(behavior.lower() for behavior in behaviors)
        mindful = state.stage in (THINKING_BEASTS, CIVILIZATION, RUIN_RENEWAL) or (
            state.variables["Ingenuity"] >= 16 and biases["Curiosity"] >= 10
        )
        summary = f"{name}. {self._behavior_sentence(behaviors)} {self.habitat_places[habitat]}"
        return SpeciesProfile(
            name=name,
            habitat=habitat,
            traits=traits,
            behaviors=behaviors,
            lineage=noun,
            summary=summary,
            mindful=mindful,
        )

    def awaken(self, state: PlanetState) -> None:
        if not state.dominant_species:
            return
        state.dominant_species.mindful = True
        state.dominant_species.summary = (
            f"{state.dominant_species.name}. It studies cause and consequence. "
            f"{self.habitat_places[state.dominant_species.habitat]}"
        )

    def _pick_habitat(self, biases: dict[str, float]) -> str:
        habitat_scores = {
            "aquatic": biases["Aquatic Bias"],
            "terrestrial": biases["Terrestrial Bias"],
            "aerial": biases["Aerial Bias"],
            "subterranean": biases["Subterranean Bias"],
        }
        ranked = sorted(habitat_scores.items(), key=lambda item: item[1], reverse=True)
        if ranked[0][0] in {"aquatic", "terrestrial"} and abs(ranked[0][1] - ranked[1][1]) < 5:
            return "amphibious"
        return ranked[0][0]

    def _pick_behaviors(self, biases: dict[str, float]) -> tuple[str, str]:
        behavior_scores = {
            key: value
            for key, value in biases.items()
            if key in {"Cooperation", "Aggression", "Adaptability", "Curiosity", "Resilience"}
        }
        ranked = sorted(behavior_scores.items(), key=lambda item: item[1], reverse=True)
        return ranked[0][0], ranked[1][0]

    def _behavior_sentence(self, behaviors: tuple[str, str]) -> str:
        first, second = behaviors
        fragments = {
            "Cooperation": "They move as many and remember together.",
            "Aggression": "They thrive through fear and contest.",
            "Adaptability": "They change before the world can break them.",
            "Curiosity": "They pry open every pattern they find.",
            "Resilience": "They persist through ruin and lean seasons.",
        }
        return f"{fragments[first]} {fragments[second]}"


class AgeSystem:
    def __init__(self, rng: random.Random, species_system: SpeciesSystem) -> None:
        self.rng = rng
        self.species_system = species_system

    def process(self, state: PlanetState, history: HistoryLog) -> list[str]:
        qualified = [
            (name, value)
            for name, value in state.variables.items()
            if abs(value) >= state.threshold_for(name)
        ]
        if len(qualified) < 3:
            return []
        drivers = sorted(
            qualified,
            key=lambda item: abs(item[1]) / state.threshold_for(item[0]),
            reverse=True,
        )[:3]
        constraints = state.lowest_variables(3)
        age_name = build_age_name(self.rng, state.stage, drivers, constraints)
        state.current_age = age_name
        state.ages_seen += 1
        history.add(state.year, state.turn, f"{age_name} begins.", "age")
        lines = [f"Age: {age_name}"]
        for variable, _ in drivers:
            if variable == "Ingenuity":
                state.ingenuity_age_threshold += 20
            else:
                state.variables[variable] = 0.0
        if state.stage != WORLDFORMING:
            state.dominant_species = self.species_system.generate(state, state.dominant_species)
            history.add(state.year, state.turn, f"{state.dominant_species.name} rises to dominance.", "species")
            lines.append(f"A new ruler appears: {state.dominant_species.name}.")
        return lines


class CivilizationSystem:
    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def process(self, state: PlanetState, history: HistoryLog) -> list[str]:
        lines: list[str] = []
        if self._should_emerge(state):
            civilization = self._create_civilization(state)
            state.civilization = civilization
            state.last_civilization_event = civilization.last_event
            history.add(state.year, state.turn, f"{civilization.name} rises from {civilization.origin_species}.", "civilization")
            lines.append(f"A civilization rises: {civilization.name}.")
            lines.append(civilization.summary)
        if not state.civilization:
            return lines
        text, effects, life_delta, stability_delta, kind = self._event_profile(state)
        state.apply_variable_changes(effects)
        state.adjust_measure(life_delta)
        state.civilization.stability = max(0, min(100, state.civilization.stability + stability_delta))
        state.civilization.last_event = text
        state.last_civilization_event = text
        state.civilization.summary = f"{state.civilization.name}. {state.civilization.ethos}. {state.civilization.focus}."
        if kind in {"war", "collapse", "renewal"}:
            history.add(state.year, state.turn, text, kind)
        lines.append(text)
        if kind == "collapse":
            state.collapse_marks += 1
        return lines

    def _should_emerge(self, state: PlanetState) -> bool:
        if state.civilization or not state.dominant_species:
            return False
        if state.stage not in (THINKING_BEASTS, CIVILIZATION, RUIN_RENEWAL):
            return False
        biases = state.derived_biases()
        if state.variables["Ingenuity"] < 16:
            return False
        chance = 0.2 + max(0.0, biases["Curiosity"]) * 0.01 + max(0.0, biases["Cooperation"]) * 0.008
        if state.stage in (CIVILIZATION, RUIN_RENEWAL):
            chance += 0.1
        return self.rng.random() < min(chance, 0.8)

    def _create_civilization(self, state: PlanetState) -> CivilizationProfile:
        biases = state.derived_biases()
        origin = state.dominant_species.name if state.dominant_species else "Forgotten Beasts"
        root = origin.split()[0]
        ethos = self._ethos_from_biases(biases)
        focus = self._focus_from_biases(state, biases)
        suffixes = {
            "kin": ["Compact", "Choir", "League", "Commonwealth"],
            "war": ["Empire", "Dominion", "Host", "Throne"],
            "craft": ["Archive", "Guild", "Forum", "Order"],
            "endure": ["Remnant", "Hearth", "House", "Keep"],
        }
        tone = "kin"
        if biases["Aggression"] > biases["Cooperation"] + 5:
            tone = "war"
        elif biases["Curiosity"] > max(biases["Aggression"], 8):
            tone = "craft"
        elif biases["Resilience"] > 8:
            tone = "endure"
        name = f"{root} {self.rng.choice(suffixes[tone])}"
        summary = f"{name}. {ethos}. {focus}."
        return CivilizationProfile(
            name=name,
            origin_species=origin,
            ethos=ethos,
            focus=focus,
            summary=summary,
            stability=55,
            last_event=f"{name} marks the land with first laws.",
        )

    def _ethos_from_biases(self, biases: dict[str, float]) -> str:
        if biases["Aggression"] > biases["Cooperation"] + 5:
            return "It honors strength and obedience"
        if biases["Curiosity"] > biases["Aggression"] and biases["Curiosity"] > 10:
            return "It honors inquiry and invention"
        if biases["Cooperation"] > 8:
            return "It honors shared burden and ritual"
        if biases["Resilience"] > 10:
            return "It honors endurance above comfort"
        return "It honors order because chaos has a long memory"

    def _focus_from_biases(self, state: PlanetState, biases: dict[str, float]) -> str:
        if state.variables["Oceans"] > 8:
            return "Its roads are made of water"
        if biases["Curiosity"] > 10:
            return "Its hunger turns toward tools and hidden laws"
        if state.variables["Dominance"] > 10:
            return "Its gaze turns toward conquest"
        if state.variables["Fertility"] < 0:
            return "Its first labor is the taming of hunger"
        return "It builds storehouses, stories, and walls"

    def _event_profile(
        self,
        state: PlanetState,
    ) -> tuple[str, dict[str, int], int, int, str]:
        biases = state.derived_biases()
        if state.stage == RUIN_RENEWAL and (state.entropy > 24 or state.civilization.stability < 35):
            return (
                f"{state.civilization.name} enters another collapse cycle.",
                {
                    "Warmth": -1,
                    "Moisture": -1,
                    "Tempest": 2,
                    "Upheaval": 2,
                    "Oceans": -1,
                    "Fertility": -3,
                    "Diversity": -3,
                    "Ingenuity": -2,
                    "Dominance": -2,
                },
                -7,
                -8,
                "collapse",
            )
        if state.life_bar < 25 and biases["Cooperation"] > biases["Aggression"]:
            return (
                f"{state.civilization.name} turns to repair and ration.",
                {
                    "Warmth": 0,
                    "Moisture": 1,
                    "Tempest": -1,
                    "Upheaval": -1,
                    "Oceans": 0,
                    "Fertility": 2,
                    "Diversity": 2,
                    "Ingenuity": 1,
                    "Dominance": -2,
                },
                4,
                5,
                "renewal",
            )
        if state.variables["Dominance"] > 10 and state.variables["Fertility"] < 0:
            return (
                f"{state.civilization.name} wages resource wars.",
                {
                    "Warmth": 1,
                    "Moisture": -1,
                    "Tempest": 1,
                    "Upheaval": 1,
                    "Oceans": 0,
                    "Fertility": -3,
                    "Diversity": -2,
                    "Ingenuity": 1,
                    "Dominance": 3,
                },
                -6,
                -6,
                "war",
            )
        if state.variables["Oceans"] > 8 and state.variables["Ingenuity"] > 12:
            return (
                f"{state.civilization.name} turns trade into rivalry.",
                {
                    "Warmth": 0,
                    "Moisture": 1,
                    "Tempest": 0,
                    "Upheaval": 0,
                    "Oceans": 2,
                    "Fertility": -1,
                    "Diversity": -1,
                    "Ingenuity": 2,
                    "Dominance": 1,
                },
                -2,
                -2,
                "war",
            )
        if biases["Curiosity"] > max(biases["Aggression"], 10):
            return (
                f"{state.civilization.name} spreads through scientific expansion.",
                {
                    "Warmth": 2,
                    "Moisture": 0,
                    "Tempest": 0,
                    "Upheaval": 1,
                    "Oceans": 1,
                    "Fertility": -2,
                    "Diversity": 1,
                    "Ingenuity": 4,
                    "Dominance": 1,
                },
                1,
                2,
                "civilization",
            )
        if biases["Aggression"] > biases["Cooperation"] + 4:
            return (
                f"{state.civilization.name} fights a war of creed and prestige.",
                {
                    "Warmth": 0,
                    "Moisture": 0,
                    "Tempest": 1,
                    "Upheaval": 1,
                    "Oceans": 0,
                    "Fertility": -1,
                    "Diversity": -2,
                    "Ingenuity": -1,
                    "Dominance": 3,
                },
                -5,
                -5,
                "war",
            )
        return (
            f"{state.civilization.name} binds distant settlements through trade and custom.",
            {
                "Warmth": 0,
                "Moisture": 1,
                "Tempest": -1,
                "Upheaval": 0,
                "Oceans": 2,
                "Fertility": 1,
                "Diversity": 1,
                "Ingenuity": 2,
                "Dominance": 0,
            },
            2,
            2,
            "civilization",
        )


class EntropySystem:
    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def advance(self, state: PlanetState) -> None:
        increment = STAGE_CONFIGS[state.stage].entropy_gain + state.collapse_marks * 0.15
        if state.civilization:
            increment += 0.25 + max(0.0, state.variables["Ingenuity"]) / 120.0
        if state.crisis_active():
            increment += 0.15
        state.entropy += increment

    def decision_factor(self, state: PlanetState, category: str) -> float:
        if category == "stabilizing":
            return max(0.35, 1.0 - state.entropy * 0.022)
        if category == "destabilizing":
            return 1.0 + state.entropy * 0.028
        return 1.0 + state.entropy * 0.012

    def apply_background_instability(self, state: PlanetState) -> list[str]:
        pressure = int(state.entropy // 7)
        if pressure <= 0:
            return []
        deltas = {
            "Warmth": self.rng.choice([0, 0, 1]),
            "Moisture": self.rng.choice([-1, 0, 0, 1]),
            "Tempest": self.rng.randint(0, pressure),
            "Upheaval": self.rng.randint(0, pressure),
            "Oceans": self.rng.choice([-1, 0, 0, 1]),
            "Fertility": -self.rng.randint(0, max(1, pressure // 2)),
            "Diversity": -self.rng.randint(0, max(1, pressure // 2)),
            "Ingenuity": 0,
            "Dominance": self.rng.randint(0, max(1, pressure // 2)),
        }
        state.apply_variable_changes(deltas)
        if state.entropy >= 14:
            return ["Old instabilities gather strength."]
        return []

    def apply_measure_drift(self, state: PlanetState) -> int:
        if state.stage == WORLDFORMING:
            score = state.worldforming_support_score()
            decay = state.entropy * 0.35
            delta = int(round(score / 8.0 - decay))
        else:
            score = state.environmental_support_score()
            decay = state.entropy * (0.45 + state.stage_index() * 0.05) + state.civilization_pressure() * 0.9
            delta = int(round(score / 7.5 - decay))
            delta -= max(0, int(state.entropy / 8) - 1)
            if state.stage in (CIVILIZATION, RUIN_RENEWAL):
                delta -= 1
        state.adjust_measure(delta)
        return delta


class StageManager:
    def __init__(
        self,
        rng: random.Random,
        species_system: SpeciesSystem,
    ) -> None:
        self.rng = rng
        self.species_system = species_system

    def process(self, state: PlanetState, history: HistoryLog) -> list[str]:
        lines: list[str] = []
        if state.stage == WORLDFORMING and state.stage_turn >= state.stage_goal:
            state.world_origin = world_origin_name(state)
            history.add(state.year, state.turn, state.world_origin, "stage")
            state.set_stage(FIRST_LIFE)
            state.habitability = max(state.habitability, 65)
            state.life_bar = max(50, min(80, state.habitability - 5))
            state.current_age = "The First Quiet"
            state.dominant_species = self.species_system.generate(state)
            history.add(state.year, state.turn, "First life takes hold.", "stage")
            history.add(state.year, state.turn, f"{state.dominant_species.name} becomes the first dominant lineage.", "species")
            lines.extend([state.world_origin, "First life takes hold."])
            return lines
        if state.stage == FIRST_LIFE and state.stage_turn >= state.stage_goal:
            state.set_stage(COMPLEX_LIFE)
            state.life_bar = max(state.life_bar, 55)
            state.current_age = "The Age of Many Shapes"
            state.dominant_species = self.species_system.generate(state, state.dominant_species)
            history.add(state.year, state.turn, "Complex life claims the world.", "stage")
            history.add(state.year, state.turn, f"{state.dominant_species.name} leads the new abundance.", "species")
            lines.extend(["Bodies grow stranger and more capable.", "Complex life claims the world."])
            return lines
        if state.stage == COMPLEX_LIFE and state.stage_turn >= state.stage_goal:
            if state.life_bar >= 35 and state.variables["Diversity"] >= 8:
                state.set_stage(GREAT_CREATURES)
                state.dominant_species = self.species_system.generate(state, state.dominant_species)
                history.add(state.year, state.turn, "Great creatures rise from the swarm of forms.", "stage")
                history.add(state.year, state.turn, f"{state.dominant_species.name} now commands the age.", "species")
                lines.append("Great creatures rise from the swarm of forms.")
        elif state.stage == GREAT_CREATURES and state.stage_turn >= state.stage_goal:
            biases = state.derived_biases()
            if state.variables["Ingenuity"] >= 14 or biases["Curiosity"] >= 12:
                state.set_stage(THINKING_BEASTS)
                self.species_system.awaken(state)
                history.add(state.year, state.turn, "Thinking beasts awaken.", "stage")
                lines.append("A beast now studies the world that made it.")
        elif state.stage == THINKING_BEASTS and state.civilization:
            state.set_stage(CIVILIZATION)
            history.add(state.year, state.turn, "Cities and laws begin to spread.", "stage")
            lines.append("Cities and laws begin to spread.")
        elif state.stage == CIVILIZATION:
            if state.entropy >= 24 or state.collapse_marks >= 2 or state.life_bar < 35:
                state.set_stage(RUIN_RENEWAL)
                history.add(state.year, state.turn, "The age turns toward ruin or renewal.", "stage")
                lines.append("The age turns toward ruin or renewal.")
        return lines
