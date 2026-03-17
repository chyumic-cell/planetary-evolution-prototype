from __future__ import annotations

import random

from .models import (
    CIVILIZATION,
    COMPLEX_LIFE,
    FIRST_LIFE,
    GREAT_CREATURES,
    RUIN_RENEWAL,
    THINKING_BEASTS,
    WORLDFORMING,
)
from .state import PlanetState


POSITIVE_SIGNS = {
    "Warmth": "Warmth settles into the ground.",
    "Moisture": "The air carries patient water.",
    "Tempest": "The winds teach bold forms to endure.",
    "Upheaval": "The deep stone keeps remaking the face of the world.",
    "Oceans": "The seas gather with long memory.",
    "Fertility": "Soil answers every fall with return.",
    "Diversity": "Life speaks in many tongues.",
    "Ingenuity": "Cunning spreads from nest to nest.",
    "Dominance": "One hunger begins to command others.",
}

NEGATIVE_SIGNS = {
    "Warmth": "Cold keeps a hard hand on the land.",
    "Moisture": "The air withholds its water.",
    "Tempest": "Storms strike without rest.",
    "Upheaval": "The ground refuses all stillness.",
    "Oceans": "The shores stand bare and far from mercy.",
    "Fertility": "The soil answers slowly.",
    "Diversity": "Too few forms remain to share the burden.",
    "Ingenuity": "Life repeats itself and learns little.",
    "Dominance": "No claimant can hold command for long.",
}

STAGE_SIGNS = {
    WORLDFORMING: "Stone, water, and fire still argue.",
    FIRST_LIFE: "Soft lives take hold in hidden places.",
    COMPLEX_LIFE: "Bodies grow strange and numerous.",
    GREAT_CREATURES: "Great bodies claim wide ground.",
    THINKING_BEASTS: "Eyes linger longer on the world.",
    CIVILIZATION: "Hands reshape what claws once spared.",
    RUIN_RENEWAL: "Old works stand beside fresh scars.",
}

AGE_PREFIXES = {
    WORLDFORMING: ("Stone", "Ash", "Tide", "Fire"),
    FIRST_LIFE: ("Spore", "Mud", "Brine", "Vent"),
    COMPLEX_LIFE: ("Shell", "Fern", "Tooth", "Wing"),
    GREAT_CREATURES: ("Beast", "Horn", "Feather", "Crown"),
    THINKING_BEASTS: ("Mind", "Hand", "Song", "Tool"),
    CIVILIZATION: ("Road", "Forge", "Archive", "Kingdom"),
    RUIN_RENEWAL: ("Ruin", "Ash", "Remnant", "Last"),
}

DRIVER_WORDS = {
    "Warmth": ("Sun", "Frost"),
    "Moisture": ("Rain", "Dust"),
    "Tempest": ("Storm", "Calm"),
    "Upheaval": ("Fire", "Still Stone"),
    "Oceans": ("Tides", "Dry Shore"),
    "Fertility": ("Bloom", "Hunger"),
    "Diversity": ("Choirs", "Silence"),
    "Ingenuity": ("Thought", "Habit"),
    "Dominance": ("Crowns", "Submission"),
}

CONSTRAINT_WORDS = {
    "Warmth": "cold ground",
    "Moisture": "dry wind",
    "Tempest": "broken weather",
    "Upheaval": "restless stone",
    "Oceans": "empty shore",
    "Fertility": "thin soil",
    "Diversity": "lonely blood",
    "Ingenuity": "forgotten craft",
    "Dominance": "unchecked hunger",
}

FINAL_LINES = (
    "The world is quiet again.",
    "What lived has returned to dust.",
    "It endured, but not forever.",
    "The long struggle has ended.",
)


def format_year(year: int) -> str:
    return f"{year:,}"


def world_signs(state: PlanetState) -> list[str]:
    lines = [STAGE_SIGNS[state.stage]]
    ranked = sorted(state.variables.items(), key=lambda item: abs(item[1]), reverse=True)
    for variable, value in ranked:
        if abs(value) < 6:
            continue
        lines.append((POSITIVE_SIGNS if value >= 0 else NEGATIVE_SIGNS)[variable])
        if len(lines) >= 3:
            break
    if len(lines) < 3:
        if state.stage == WORLDFORMING:
            lines.append("The sky waits for its final temper.")
        elif state.dominant_species:
            lines.append(f"{state.dominant_species.name} carries the age forward.")
        else:
            lines.append("Life keeps to the margins and persists.")
    if state.entropy >= 18 and len(lines) < 4:
        lines.append("What is settled begins to fray.")
    return lines[:3]


def build_age_name(
    rng: random.Random,
    stage: str,
    drivers: list[tuple[str, float]],
    constraints: list[tuple[str, float]],
) -> str:
    prefix = rng.choice(AGE_PREFIXES[stage])
    first_var, first_value = drivers[0]
    second_var, second_value = drivers[1]
    first_word = DRIVER_WORDS[first_var][0 if first_value >= 0 else 1]
    second_word = DRIVER_WORDS[second_var][0 if second_value >= 0 else 1]
    if constraints and constraints[0][1] < 0:
        constraint = CONSTRAINT_WORDS[constraints[0][0]].title()
        return f"The {prefix} Age of {first_word} and {constraint}"
    return f"The {prefix} Age of {first_word} and {second_word}"


def world_origin_name(state: PlanetState) -> str:
    values = state.variables
    if values["Oceans"] > 12 and values["Moisture"] > 8:
        return "An ocean world has opened its first cradle."
    if values["Moisture"] > 10 and values["Fertility"] > 8:
        return "A swamp world steams with promise."
    if values["Moisture"] < -8 and values["Warmth"] > 4:
        return "A dry basin world keeps its mercy in rare places."
    if values["Tempest"] > 12:
        return "A storm heavy world learns through violence."
    if values["Upheaval"] > 12:
        return "A geothermal world glows from below."
    return "A temperate cradle has taken shape."


def describe_outcome(tag: str, measure_delta: int) -> str:
    if measure_delta >= 8:
        return "The world answers with strength."
    if measure_delta >= 3:
        return "The touch brings a season of relief."
    if measure_delta >= 0:
        return "The gain is real. The cost remains."
    if measure_delta >= -5:
        return "The price is felt at once."
    if tag == "destabilizing":
        return "Correction comes hard and fast."
    return "The wound opens wider."


def final_epitaph(state: PlanetState) -> str:
    line = state.rng.choice(FINAL_LINES)
    if state.civilization:
        return f"{state.civilization.name} is gone. {line}"
    if state.dominant_species:
        return f"{state.dominant_species.name} has fallen. {line}"
    return line


def civilization_sign(state: PlanetState) -> str:
    if not state.civilization:
        return "No city has found its voice."
    if state.stage == RUIN_RENEWAL:
        return f"{state.civilization.name} lives among ruins and stubborn memory."
    if state.stage == CIVILIZATION:
        return f"{state.civilization.name} stretches its reach across the land."
    return state.civilization.summary
