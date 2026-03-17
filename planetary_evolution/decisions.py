from __future__ import annotations

import random
from dataclasses import dataclass

from .models import (
    CIVILIZATION,
    COMPLEX_LIFE,
    FIRST_LIFE,
    GREAT_CREATURES,
    RUIN_RENEWAL,
    THINKING_BEASTS,
    VARIABLES,
    WORLDFORMING,
    DecisionArchetype,
    DecisionOption,
    DelayedEffectTemplate,
    PendingEffect,
)
from .state import PlanetState


@dataclass(frozen=True)
class FamilyBlueprint:
    key: str
    category: str
    effects: dict[str, int]
    life_delta: int
    tags: tuple[str, ...]
    delayed: tuple[DelayedEffectTemplate, ...]
    line_pool_a: tuple[str, ...]
    line_pool_b: tuple[str, ...]
    line_pool_c: tuple[str, ...]
    titles: dict[str, str]
    compatible_stages: dict[str, tuple[str, ...]]


INTENSITY_SCALE = {1: 0.85, 2: 1.0, 3: 1.25}
ALL_BANDS = {
    "early": (WORLDFORMING, FIRST_LIFE),
    "mid": (COMPLEX_LIFE, GREAT_CREATURES, THINKING_BEASTS),
    "late": (CIVILIZATION, RUIN_RENEWAL),
}


def _full_effects(**values: int) -> dict[str, int]:
    return {variable: values.get(variable, 0) for variable in VARIABLES}


def _template(min_delay: int, max_delay: int, life_delta: int, texts: tuple[str, ...], **values: int) -> DelayedEffectTemplate:
    return DelayedEffectTemplate(
        min_delay=min_delay,
        max_delay=max_delay,
        variable_deltas=_full_effects(**values),
        life_delta=life_delta,
        texts=texts,
    )


class DecisionGenerator:
    def __init__(self, rng: random.Random) -> None:
        self.rng = rng
        self.archetypes = self._build_archetypes()
        self.last_candidate_count = 0

    def archetype_count(self) -> int:
        return len(self.archetypes)

    def generate_choices(self, state: PlanetState) -> list[DecisionOption]:
        compatible = [a for a in self.archetypes if state.stage in a.compatible_stages]
        category_pools = {
            "stabilizing": [a for a in compatible if a.category == "stabilizing"],
            "destabilizing": [a for a in compatible if a.category == "destabilizing"],
            "ambiguous": [a for a in compatible if a.category == "ambiguous"],
        }

        candidate_target = self.rng.randint(10, 15)
        candidates: list[DecisionOption] = []
        for category, minimum in (("stabilizing", 3), ("destabilizing", 3), ("ambiguous", 3)):
            pool = category_pools[category]
            pick_count = min(len(pool), minimum + self.rng.randint(0, 1))
            candidates.extend(self._instantiate_many(state, pool, pick_count))

        while len(candidates) < candidate_target:
            chosen_category = self.rng.choices(
                population=["stabilizing", "destabilizing", "ambiguous"],
                weights=self._category_weights(state),
                k=1,
            )[0]
            pool = category_pools[chosen_category]
            candidates.extend(self._instantiate_many(state, pool, 1))

        self.last_candidate_count = len(candidates)
        return [
            self._filter_choice(state, candidates, "stabilizing"),
            self._filter_choice(state, candidates, "destabilizing"),
            self._filter_choice(state, candidates, "ambiguous"),
        ]

    def _category_weights(self, state: PlanetState) -> tuple[int, int, int]:
        if state.crisis_active():
            return (6, 2, 5)
        return (4, 4, 4)

    def _instantiate_many(
        self,
        state: PlanetState,
        pool: list[DecisionArchetype],
        count: int,
    ) -> list[DecisionOption]:
        if not pool or count <= 0:
            return []
        weighted = [(archetype, self._archetype_weight(state, archetype)) for archetype in pool]
        result: list[DecisionOption] = []
        for _ in range(count):
            archetype = self.rng.choices(
                population=[item[0] for item in weighted],
                weights=[item[1] for item in weighted],
                k=1,
            )[0]
            result.append(self._instantiate(state, archetype))
        return result

    def _archetype_weight(self, state: PlanetState, archetype: DecisionArchetype) -> float:
        weight = 1.0
        if state.crisis_active() and "recovery" in archetype.tags:
            weight += 3.5
        if state.stage in (CIVILIZATION, RUIN_RENEWAL) and "civic" in archetype.tags:
            weight += 1.5
        if state.stage == WORLDFORMING and "primordial" in archetype.tags:
            weight += 1.5
        if state.stage in (GREAT_CREATURES, THINKING_BEASTS) and "evolution" in archetype.tags:
            weight += 1.0
        if archetype.category == "destabilizing" and state.crisis_active():
            weight *= 0.7
        return max(weight, 0.1)

    def _instantiate(self, state: PlanetState, archetype: DecisionArchetype) -> DecisionOption:
        intensity = self.rng.choices(population=[1, 2, 3], weights=[3, 4, 3], k=1)[0]
        scale = INTENSITY_SCALE[intensity]
        immediate_effects = {
            variable: int(round(amount * scale))
            for variable, amount in archetype.effects.items()
        }
        immediate_life_delta = int(round(archetype.life_delta * scale))
        pending_effects: list[PendingEffect] = []
        for template in archetype.delayed_templates:
            delay = self.rng.randint(template.min_delay, template.max_delay)
            pending_effects.append(
                PendingEffect(
                    due_turn=state.turn + delay,
                    variable_deltas={
                        variable: int(round(amount * scale))
                        for variable, amount in template.variable_deltas.items()
                    },
                    life_delta=int(round(template.life_delta * scale)),
                    text=self.rng.choice(template.texts),
                    source_title=archetype.title,
                )
            )
        return DecisionOption(
            archetype_key=archetype.key,
            title=archetype.title,
            category=archetype.category,
            intensity=intensity,
            text_lines=(
                self.rng.choice(archetype.line_pool_a),
                self.rng.choice(archetype.line_pool_b),
                self.rng.choice(archetype.line_pool_c),
            ),
            immediate_effects=immediate_effects,
            immediate_life_delta=immediate_life_delta,
            pending_effects=pending_effects,
            tags=archetype.tags,
        )

    def _filter_choice(
        self,
        state: PlanetState,
        candidates: list[DecisionOption],
        category: str,
    ) -> DecisionOption:
        pool = [candidate for candidate in candidates if candidate.category == category]
        ranked = sorted(pool, key=lambda option: self._score_option(state, option), reverse=True)
        top = ranked[: max(1, min(3, len(ranked)))]
        return self.rng.choice(top)

    def _score_option(self, state: PlanetState, option: DecisionOption) -> float:
        positive = sum(max(0, amount) for amount in option.immediate_effects.values())
        negative = sum(abs(min(0, amount)) for amount in option.immediate_effects.values())
        volatility = positive + negative
        if option.category == "stabilizing":
            score = (
                option.immediate_life_delta * 2
                + positive
                - max(0, option.immediate_effects["Tempest"])
                - max(0, option.immediate_effects["Upheaval"])
                - max(0, option.immediate_effects["Dominance"])
            )
            if state.crisis_active() and "recovery" in option.tags:
                score += 10
            return score
        if option.category == "destabilizing":
            return volatility + option.immediate_effects["Ingenuity"] + option.immediate_effects["Fertility"]
        mixed = min(positive, negative)
        score = mixed + abs(option.immediate_life_delta) + volatility * 0.3
        if state.crisis_active() and "recovery" in option.tags:
            score += 6
        return score

    def _build_archetypes(self) -> list[DecisionArchetype]:
        families = self._family_blueprints()
        archetypes: list[DecisionArchetype] = []
        for family in families:
            for band, title in family.titles.items():
                archetypes.append(
                    DecisionArchetype(
                        key=f"{family.key}_{band}",
                        title=title,
                        category=family.category,
                        compatible_stages=family.compatible_stages[band],
                        effects=family.effects,
                        life_delta=family.life_delta,
                        delayed_templates=family.delayed,
                        tags=family.tags,
                        line_pool_a=family.line_pool_a,
                        line_pool_b=family.line_pool_b,
                        line_pool_c=family.line_pool_c,
                    )
                )
        return archetypes

    def _family_blueprints(self) -> list[FamilyBlueprint]:
        return [
            FamilyBlueprint(
                key="tide_guidance",
                category="stabilizing",
                effects=_full_effects(Warmth=-1, Moisture=3, Tempest=-2, Upheaval=-1, Oceans=3, Fertility=2, Diversity=1, Ingenuity=1, Dominance=-1),
                life_delta=5,
                tags=("water", "recovery", "primordial"),
                delayed=(
                    _template(3, 4, 2, ("Quiet deltas spread their gift.", "The shallows keep new abundance."), Oceans=1, Fertility=2, Diversity=1),
                ),
                line_pool_a=("The waters accept a patient command.", "A slow pull gathers the seas.", "The coasts listen at last."),
                line_pool_b=("Channels remember their course.", "Wet ground finds its shape.", "Flood and shore part with grace."),
                line_pool_c=("What follows will have room to breathe.", "Life will find easier shelter.", "Mercy settles near the tide."),
                titles={"early": "Calling the Tides", "mid": "River Memory", "late": "Canals of Mercy"},
                compatible_stages={"early": (WORLDFORMING, FIRST_LIFE), "mid": ALL_BANDS["mid"], "late": ALL_BANDS["late"]},
            ),
            FamilyBlueprint(
                key="ash_gardens",
                category="stabilizing",
                effects=_full_effects(Warmth=1, Moisture=-1, Tempest=1, Upheaval=2, Oceans=0, Fertility=4, Diversity=2, Ingenuity=0, Dominance=-1),
                life_delta=3,
                tags=("stone", "recovery", "primordial"),
                delayed=(
                    _template(2, 4, 3, ("Old ash cools into rich ground.", "The blackened crust begins to feed."), Upheaval=-2, Fertility=3, Diversity=2),
                ),
                line_pool_a=("Fire leaves more than ruin.", "Ash falls and does not lie idle.", "The scorched earth keeps a hidden kindness."),
                line_pool_b=("Dark soil gathers strength.", "What burned settles into promise.", "The wound prepares a feast."),
                line_pool_c=("Hunger softens where the ash rests.", "Many mouths will profit later.", "The future feeds on this grief."),
                titles={"early": "Ashen Seeding", "mid": "Black Soil Bargain", "late": "Fields of Cinder"},
                compatible_stages={"early": (WORLDFORMING, FIRST_LIFE), "mid": ALL_BANDS["mid"], "late": ALL_BANDS["late"]},
            ),
            FamilyBlueprint(
                key="patient_rains",
                category="stabilizing",
                effects=_full_effects(Warmth=-2, Moisture=4, Tempest=-1, Upheaval=-1, Oceans=1, Fertility=2, Diversity=2, Ingenuity=0, Dominance=-1),
                life_delta=4,
                tags=("weather", "recovery", "primordial"),
                delayed=(
                    _template(3, 5, -2, ("Water lingers too long in the low places.", "Soft ground gives way beneath plenty."), Moisture=1, Tempest=2, Dominance=1),
                ),
                line_pool_a=("Clouds are called to patience.", "The sky remembers to give.", "Rain returns with a softer hand."),
                line_pool_b=("Dry places drink deeply.", "Rills run where dust once ruled.", "The cracked ground loosens."),
                line_pool_c=("Relief arrives. So does burden.", "Abundance comes with weight.", "Plenty asks to be managed."),
                titles={"early": "Calling the Gentle Rains", "mid": "Season of Soft Rivers", "late": "Reservoir Prayer"},
                compatible_stages={"early": (WORLDFORMING, FIRST_LIFE), "mid": ALL_BANDS["mid"], "late": ALL_BANDS["late"]},
            ),
            FamilyBlueprint(
                key="sheltered_roots",
                category="stabilizing",
                effects=_full_effects(Warmth=0, Moisture=1, Tempest=-2, Upheaval=-1, Oceans=-1, Fertility=3, Diversity=2, Ingenuity=1, Dominance=-2),
                life_delta=4,
                tags=("shelter", "recovery", "evolution"),
                delayed=(
                    _template(2, 4, 2, ("Hidden nests hold against the season.", "Shelter teaches endurance."), Fertility=2, Diversity=1, Dominance=-1),
                ),
                line_pool_a=("Protection is raised in quiet places.", "A small refuge is carved from danger.", "The weak are given cover."),
                line_pool_b=("Roots thicken beneath the calm.", "The hidden chambers fill with life.", "Eggs and seeds pass unseen."),
                line_pool_c=("What survives here will spread later.", "Endurance grows in shade.", "The spared will remember."),
                titles={"early": "Sheltered Pools", "mid": "Rooted Havens", "late": "Storehouses of Seed"},
                compatible_stages={"early": (FIRST_LIFE,), "mid": ALL_BANDS["mid"], "late": ALL_BANDS["late"]},
            ),
            FamilyBlueprint(
                key="kin_bonds",
                category="stabilizing",
                effects=_full_effects(Warmth=0, Moisture=0, Tempest=-1, Upheaval=-1, Oceans=1, Fertility=1, Diversity=3, Ingenuity=2, Dominance=-3),
                life_delta=3,
                tags=("social", "recovery", "evolution", "civic"),
                delayed=(
                    _template(2, 5, 1, ("Shared memory outlives the moment.", "The lesson passes from many to many."), Diversity=1, Ingenuity=2, Dominance=-1),
                ),
                line_pool_a=("The many are taught to lean on one another.", "A common rhythm is strengthened.", "Strangers are made into kin."),
                line_pool_b=("Food, warning, and shelter are shared.", "Burden spreads across many backs.", "The lone hunger is checked."),
                line_pool_c=("Strength arrives through company.", "The chorus thickens.", "A gentler order takes root."),
                titles={"early": "First Colonies", "mid": "Binding the Clans", "late": "Common Oaths"},
                compatible_stages={"early": (FIRST_LIFE,), "mid": ALL_BANDS["mid"], "late": ALL_BANDS["late"]},
            ),
            FamilyBlueprint(
                key="tectonic_rend",
                category="destabilizing",
                effects=_full_effects(Warmth=2, Moisture=-2, Tempest=2, Upheaval=4, Oceans=-1, Fertility=-3, Diversity=-2, Ingenuity=1, Dominance=1),
                life_delta=-6,
                tags=("stone", "primordial"),
                delayed=(
                    _template(3, 4, 1, ("Fresh minerals lie open to the weather.", "The torn crust feeds what comes after."), Moisture=1, Fertility=3, Upheaval=-1),
                ),
                line_pool_a=("The ground shifts beneath all certainty.", "Stone refuses its old oath.", "The deep rises in anger."),
                line_pool_b=("What is buried comes to light.", "Mountains answer the call.", "Foundations fail where they once held."),
                line_pool_c=("What stands may fall.", "The wound will alter every path.", "No living thing is spared the shaking."),
                titles={"early": "Cracking Earth", "mid": "Restless Crust", "late": "Shattered Foundations"},
                compatible_stages={"early": (WORLDFORMING, FIRST_LIFE), "mid": ALL_BANDS["mid"], "late": ALL_BANDS["late"]},
            ),
            FamilyBlueprint(
                key="scorching_skies",
                category="destabilizing",
                effects=_full_effects(Warmth=4, Moisture=-3, Tempest=2, Upheaval=0, Oceans=-2, Fertility=-2, Diversity=-2, Ingenuity=1, Dominance=2),
                life_delta=-5,
                tags=("heat", "primordial"),
                delayed=(
                    _template(2, 4, -2, ("The heat lingers after the blaze.", "The parched season does not release its grip."), Tempest=1, Diversity=-1, Ingenuity=1),
                ),
                line_pool_a=("The sky keeps too much fire.", "Heat gathers and does not leave.", "The day turns sharp and cruel."),
                line_pool_b=("Water flees from leaf and lung.", "Shade grows precious.", "Soft things begin to curl."),
                line_pool_c=("Survival will belong to the hard.", "The weak will burn first.", "Only stern forms will remain."),
                titles={"early": "Scorching Sky", "mid": "Season of Hard Sun", "late": "The Furnace Years"},
                compatible_stages={"early": (WORLDFORMING, FIRST_LIFE), "mid": ALL_BANDS["mid"], "late": ALL_BANDS["late"]},
            ),
            FamilyBlueprint(
                key="black_flood",
                category="destabilizing",
                effects=_full_effects(Warmth=-1, Moisture=4, Tempest=3, Upheaval=1, Oceans=3, Fertility=-2, Diversity=-3, Ingenuity=0, Dominance=1),
                life_delta=-6,
                tags=("water", "primordial"),
                delayed=(
                    _template(3, 5, 2, ("When the waters fall, rich silt remains.", "Retreating floods leave dark nourishment behind."), Oceans=1, Fertility=2),
                ),
                line_pool_a=("The waters rise without mercy.", "River and sea forget their bounds.", "The low places vanish beneath the surge."),
                line_pool_b=("Old nests drown.", "The land gives way to the deep.", "What cannot float is taken."),
                line_pool_c=("The world will be redrawn by water.", "Many will perish before the new shore is known.", "Only the swift and the hidden endure."),
                titles={"early": "The Black Flood", "mid": "Drowning Season", "late": "Deluge of the Lowlands"},
                compatible_stages={"early": (WORLDFORMING, FIRST_LIFE), "mid": ALL_BANDS["mid"], "late": ALL_BANDS["late"]},
            ),
            FamilyBlueprint(
                key="predator_release",
                category="destabilizing",
                effects=_full_effects(Warmth=1, Moisture=-1, Tempest=0, Upheaval=0, Oceans=0, Fertility=-2, Diversity=-3, Ingenuity=2, Dominance=4),
                life_delta=-5,
                tags=("predation", "evolution"),
                delayed=(
                    _template(3, 5, 1, ("The hunted grow sharper in the shadow of teeth.", "Fear teaches quick limbs and quicker minds."), Fertility=2, Diversity=1, Dominance=-1),
                ),
                line_pool_a=("A new hunter is given leave to thrive.", "Fangs and patience are favored.", "The chase grows crueler."),
                line_pool_b=("Herd and flock learn terror.", "The weak vanish first.", "Feeding grounds empty in haste."),
                line_pool_c=("Balance will return only after blood.", "The lesson is brutal and clear.", "The age of fear begins."),
                titles={"early": "Feeding the First Hunter", "mid": "Release the Great Predator", "late": "The Teeth of Empire"},
                compatible_stages={"early": (FIRST_LIFE,), "mid": ALL_BANDS["mid"], "late": ALL_BANDS["late"]},
            ),
            FamilyBlueprint(
                key="iron_hunger",
                category="destabilizing",
                effects=_full_effects(Warmth=3, Moisture=-1, Tempest=1, Upheaval=2, Oceans=-1, Fertility=-3, Diversity=-2, Ingenuity=3, Dominance=2),
                life_delta=-4,
                tags=("civic", "extraction", "primordial"),
                delayed=(
                    _template(2, 4, -3, ("The taking does not slow once it begins.", "Appetite learns its own momentum."), Ingenuity=2, Dominance=1, Fertility=-2),
                ),
                line_pool_a=("The deep stores are torn open.", "Hidden strength is drawn from the earth.", "Heavy wealth is brought to hand."),
                line_pool_b=("Craft grows bold on stolen ground.", "Power answers the taking.", "The work leaves scars behind it."),
                line_pool_c=("Gain comes first. Reckoning follows.", "The earth keeps count of every theft.", "Prosperity sharpens its own knife."),
                titles={"early": "Drawing the Heavy Metals", "mid": "The Iron Hunger", "late": "Mines Without End"},
                compatible_stages={"early": (WORLDFORMING,), "mid": ALL_BANDS["mid"], "late": ALL_BANDS["late"]},
            ),
            FamilyBlueprint(
                key="restless_winds",
                category="ambiguous",
                effects=_full_effects(Warmth=0, Moisture=1, Tempest=4, Upheaval=-1, Oceans=1, Fertility=0, Diversity=1, Ingenuity=2, Dominance=0),
                life_delta=-1,
                tags=("weather", "primordial", "recovery"),
                delayed=(
                    _template(2, 4, 2, ("After the violence, scattered seeds take root.", "The broken weather leaves strange chances behind."), Tempest=-2, Diversity=2),
                ),
                line_pool_a=("The winds are urged into unrest.", "The air is given a sharper edge.", "The sky is set loose from restraint."),
                line_pool_b=("Spores, ash, and scent travel far.", "Nothing remains in its first place.", "The horizon grows loud."),
                line_pool_c=("Destruction and dispersal arrive together.", "The cost is swift. The reach is wide.", "Chance spreads on the storm."),
                titles={"early": "Restless Winds", "mid": "Storm Roads", "late": "Tempest Couriers"},
                compatible_stages={"early": (WORLDFORMING, FIRST_LIFE), "mid": ALL_BANDS["mid"], "late": ALL_BANDS["late"]},
            ),
            FamilyBlueprint(
                key="daring_migration",
                category="ambiguous",
                effects=_full_effects(Warmth=1, Moisture=0, Tempest=1, Upheaval=0, Oceans=1, Fertility=-1, Diversity=2, Ingenuity=2, Dominance=1),
                life_delta=1,
                tags=("evolution", "recovery"),
                delayed=(
                    _template(3, 5, -2, ("The newcomers crowd what was already claimed.", "Shared ground turns tense after the wandering."), Dominance=2, Diversity=-2),
                ),
                line_pool_a=("The people of one place are sent into another.", "Migration is opened as a path.", "Old borders are ignored."),
                line_pool_b=("Fresh food and danger wait beyond the ridge.", "New waters promise survival and rivalry.", "Empty land calls to the bold."),
                line_pool_c=("Expansion carries seed and conflict alike.", "A wider world asks a harder price.", "The journey solves one hunger and creates another."),
                titles={"early": "Sending the First Drifters", "mid": "The Great Migration", "late": "Opening New Frontiers"},
                compatible_stages={"early": (FIRST_LIFE,), "mid": ALL_BANDS["mid"], "late": ALL_BANDS["late"]},
            ),
            FamilyBlueprint(
                key="awakened_fire",
                category="ambiguous",
                effects=_full_effects(Warmth=2, Moisture=-1, Tempest=1, Upheaval=2, Oceans=0, Fertility=1, Diversity=-1, Ingenuity=3, Dominance=2),
                life_delta=0,
                tags=("fire", "recovery", "evolution", "civic", "primordial"),
                delayed=(
                    _template(2, 5, 2, ("Mastered heat feeds those who survive it.", "The burn leaves tools and richer ground."), Fertility=2, Ingenuity=1, Tempest=1),
                ),
                line_pool_a=("Flame is welcomed rather than feared.", "Fire is invited into the order of things.", "The bright hunger is given purpose."),
                line_pool_b=("Cold retreats. Shelter and risk grow together.", "New craft is born beside old danger.", "The gift cuts both hand and darkness."),
                line_pool_c=("Power has entered the world.", "What follows will not be simple.", "Creation and ruin now share a spark."),
                titles={"early": "Awakened Fire", "mid": "Fire Kept in Hand", "late": "The Furnace Pact"},
                compatible_stages={"early": (WORLDFORMING, FIRST_LIFE), "mid": ALL_BANDS["mid"], "late": ALL_BANDS["late"]},
            ),
            FamilyBlueprint(
                key="forbidden_synthesis",
                category="ambiguous",
                effects=_full_effects(Warmth=0, Moisture=1, Tempest=0, Upheaval=1, Oceans=1, Fertility=1, Diversity=3, Ingenuity=4, Dominance=1),
                life_delta=1,
                tags=("recovery", "evolution", "civic", "primordial"),
                delayed=(
                    _template(3, 5, -4, ("The new form spreads faster than wisdom.", "A gift without restraint turns ravenous."), Dominance=2, Diversity=-3, Tempest=1),
                ),
                line_pool_a=("Elements that were apart are urged together.", "Strange unions are permitted.", "The old boundaries of form are crossed."),
                line_pool_b=("Novel bodies and habits emerge.", "Life learns a path it did not deserve.", "What was impossible begins to breed."),
                line_pool_c=("Great promise walks beside great peril.", "The blessing carries a hidden fang.", "The world will judge this mingling later."),
                titles={"early": "Primordial Synthesis", "mid": "Hybrid Bloodlines", "late": "Borrowed Flesh"},
                compatible_stages={"early": (WORLDFORMING, FIRST_LIFE), "mid": ALL_BANDS["mid"], "late": ALL_BANDS["late"]},
            ),
        ]
