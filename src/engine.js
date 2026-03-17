
import {
  CIVILIZATION_SUFFIXES,
  DECISION_TEMPLATES,
  FINAL_LINES,
  SEVERITIES,
  SPECIES_POOLS,
  STAGE_CONFIGS,
  STAGE_ORDER,
  SWARM_SUFFIXES,
  VARIABLES,
} from './game-data.js';

const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
const randomInt = (rng, min, max) => Math.floor(rng() * (max - min + 1)) + min;
const pick = (rng, values) => values[Math.floor(rng() * values.length)];

const visibleStageSigns = {
  Worldforming: 'Stone, weather, and ocean still argue.',
  'First Life': 'Small lives cling to edges and vents.',
  'Complex Life': 'Bodies diversify and claim new ground.',
  'Great Creatures': 'Great bodies press their weight upon the world.',
  'Thinking Beasts': 'Eyes linger on patterns and consequences.',
  Civilization: 'Hands, roads, and walls begin to matter.',
  'Ruin or Renewal': 'Old works survive beside fresh scars.',
};

const positiveSigns = {
  Warmth: 'Warmth settles into the land.',
  Moisture: 'The air carries patient water.',
  Tempest: 'The winds move with force and reach.',
  Upheaval: 'The deep stone keeps remaking the face of the world.',
  Oceans: 'The seas gather with long memory.',
  Fertility: 'Soil answers with return.',
  Diversity: 'Life speaks in many tongues.',
  Ingenuity: 'Patterns are noticed and reused.',
  Dominance: 'One hunger grows strong over others.',
};

const negativeSigns = {
  Warmth: 'Cold keeps a hard hand on the surface.',
  Moisture: 'Dryness lingers too long.',
  Tempest: 'Storms refuse to rest.',
  Upheaval: 'The ground rejects stillness.',
  Oceans: 'The shores stand bare and far from mercy.',
  Fertility: 'The soil answers slowly.',
  Diversity: 'Too few forms remain to share the burden.',
  Ingenuity: 'Life repeats itself and learns little.',
  Dominance: 'No claimant can hold command for long.',
};

const ageWords = {
  Warmth: ['Sun', 'Frost'],
  Moisture: ['Rain', 'Dust'],
  Tempest: ['Storm', 'Calm'],
  Upheaval: ['Fire', 'Still Stone'],
  Oceans: ['Tides', 'Dry Shore'],
  Fertility: ['Bloom', 'Hunger'],
  Diversity: ['Choirs', 'Silence'],
  Ingenuity: ['Thought', 'Habit'],
  Dominance: ['Crowns', 'Submission'],
};

const agePrefixes = {
  Worldforming: ['Stone', 'Ash', 'Tide', 'Fire'],
  'First Life': ['Spore', 'Mud', 'Brine', 'Vent'],
  'Complex Life': ['Shell', 'Fern', 'Wing', 'Tooth'],
  'Great Creatures': ['Crown', 'Horn', 'Feather', 'Beast'],
  'Thinking Beasts': ['Mind', 'Hand', 'Song', 'Tool'],
  Civilization: ['Road', 'Forge', 'Archive', 'Kingdom'],
  'Ruin or Renewal': ['Ruin', 'Remnant', 'Ash', 'Last'],
};

const habitatDescriptions = {
  aquatic: 'It commands the water.',
  amphibious: 'It thrives where water and land trade places.',
  terrestrial: 'It dominates broad land and open plain.',
  aerial: 'It claims the high air and exposed cliffs.',
  subterranean: 'It prospers beneath the world others see.',
};

const civEthos = {
  kin: 'It honors shared burden and ritual.',
  war: 'It honors strength and obedience.',
  craft: 'It honors inquiry and invention.',
  endure: 'It honors endurance above comfort.',
  order: 'It honors order because chaos has a long memory.',
};

const bugPattern = /(Ant|Moth|Beetle|Scarab|Locust|Chitin|Hive|Swarm)/i;

const lineageOrigins = {
  fish: 'fish',
  shark: 'sharks',
  bird: 'birds',
  bug: 'bugs',
  grazer: 'grazers',
  primate: 'primates',
  reptile: 'reptiles',
  sloth: 'sloths',
};

const lineageNouns = {
  fish: ['Fins', 'Eels', 'Shoals'],
  shark: ['Sharks'],
  bird: ['Herons', 'Kites', 'Larks', 'Wings'],
  bug: ['Ants', 'Scarabs', 'Moths', 'Locusts'],
  grazer: ['Deer', 'Browsers', 'Harts'],
  primate: ['Monkeys', 'Apes'],
  reptile: ['Lizards', 'Drakes'],
  sloth: ['Sloths'],
};

const habitatPrefixes = {
  aquatic: ['Sea', 'Reef', 'Tide'],
  amphibious: ['Marsh', 'Delta', 'Shore'],
  terrestrial: ['Plain', 'Stone', 'Forest'],
  aerial: ['Sky', 'Cloud', 'Storm'],
  subterranean: ['Burrow', 'Root', 'Deep'],
};

const naturalLineageHabitats = {
  fish: 'aquatic',
  shark: 'aquatic',
  bird: 'aerial',
  bug: 'subterranean',
  grazer: 'terrestrial',
  primate: 'terrestrial',
  reptile: 'terrestrial',
  sloth: 'terrestrial',
};

const effectPhrases = {
  Warmth: ['warmer seasons', 'harder cold'],
  Moisture: ['wetter air', 'drier air'],
  Tempest: ['rougher storms', 'quieter skies'],
  Upheaval: ['restless stone', 'steadier ground'],
  Oceans: ['broader seas', 'retreating seas'],
  Fertility: ['richer soil', 'hungrier soil'],
  Diversity: ['more varied life', 'narrower ecosystems'],
  Ingenuity: ['sharper pattern seeking', 'slower learning'],
  Dominance: ['stronger rival claimants', 'softer rival claims'],
};

function createRng(seed) {
  let value = seed % 2147483647;
  if (value <= 0) value += 2147483646;
  return () => {
    value = (value * 16807) % 2147483647;
    return (value - 1) / 2147483646;
  };
}

function strongestEffects(effects) {
  return Object.entries(effects)
    .filter(([, value]) => value !== 0)
    .sort((left, right) => Math.abs(right[1]) - Math.abs(left[1]));
}

function describeDecisionEffects(effects) {
  const ranked = strongestEffects(effects);
  if (!ranked.length) return 'The world shifts in subtle ways.';
  const [mainKey, mainValue] = ranked[0];
  const [secondKey, secondValue] = ranked[1] ?? ranked[0];
  const positive = mainValue >= 0 ? effectPhrases[mainKey][0] : effectPhrases[mainKey][1];
  const tradeoff = secondValue >= 0 ? effectPhrases[secondKey][0] : effectPhrases[secondKey][1];
  return `Leans toward ${positive}. Risks ${tradeoff}.`;
}

function describeMeasure(value, stage) {
  if (stage === 'Worldforming') {
    if (value >= 85) return 'The world is welcoming.';
    if (value >= 65) return 'The world can bear life.';
    if (value >= 45) return 'The world leans toward mercy.';
    if (value >= 25) return 'The world is harsh.';
    return 'The world resists the seed.';
  }
  if (value >= 85) return 'Life is abundant.';
  if (value >= 65) return 'Life endures with strength.';
  if (value >= 45) return 'Life holds its ground.';
  if (value >= 25) return 'Life bends under strain.';
  if (value > 0) return 'Life clings by its nails.';
  return 'Life has fallen silent.';
}

function stageOriginDescription(values) {
  if (values.Oceans > 12 && values.Moisture > 8) return 'An ocean world opens its first cradle.';
  if (values.Moisture > 9 && values.Fertility > 8) return 'A swamp world steams with promise.';
  if (values.Moisture < -8 && values.Warmth > 4) return 'A dry basin world keeps its mercy in rare places.';
  if (values.Tempest > 12) return 'A storm heavy world learns through violence.';
  if (values.Upheaval > 12) return 'A geothermal world glows from below.';
  return 'A temperate cradle takes shape.';
}

export class HistoryLog {
  constructor(limit = 8) {
    this.limit = limit;
    this.entries = [];
  }

  add(year, turn, kind, text) {
    this.entries.push({ year, turn, kind, text });
    if (this.entries.length > 40) this.entries.shift();
  }

  recent() {
    return this.entries.slice(-this.limit).reverse();
  }
}

export class DelayedEffectQueue {
  constructor() {
    this.items = [];
  }

  addMany(effects) {
    this.items.push(...effects);
  }

  resolve(turn) {
    const due = this.items.filter((item) => item.turn <= turn);
    this.items = this.items.filter((item) => item.turn > turn);
    return due;
  }
}

export class PlanetState {
  constructor(rng) {
    this.rng = rng;
    this.stage = 'Worldforming';
    this.turn = 0;
    this.year = 0;
    this.stageTurn = 0;
    this.stageGoal = 0;
    this.habitability = 34;
    this.life = 0;
    this.variables = Object.fromEntries(VARIABLES.map((variable) => [variable, 0]));
    this.entropy = 0;
    this.currentAge = 'The Silent Cradle';
    this.worldOrigin = 'Stone waits beneath a patient sun.';
    this.dominantSpecies = null;
    this.civilization = null;
    this.recentConsequences = ['The world waits for your first shaping.'];
    this.collapseMarks = 0;
    this.recoveries = 0;
    this.inCrisis = false;
    this.ageCount = 0;
    this.mindEchoes = 0;
    this.extinct = false;
    this.finalText = '';
    this.resetStageGoal();
  }

  resetStageGoal() {
    const [minGoal, maxGoal] = STAGE_CONFIGS[this.stage].goal;
    this.stageGoal = randomInt(this.rng, minGoal, maxGoal);
  }

  setStage(nextStage) {
    this.stage = nextStage;
    this.stageTurn = 0;
    this.resetStageGoal();
  }

  advanceClock() {
    this.turn += 1;
    this.stageTurn += 1;
    const [minYears, maxYears] = STAGE_CONFIGS[this.stage].years;
    this.year += randomInt(this.rng, minYears, maxYears);
  }

  stageIndex() {
    return STAGE_ORDER.indexOf(this.stage);
  }

  meterName() {
    return this.stage === 'Worldforming' ? 'Habitability' : 'Life';
  }

  meterValue() {
    return this.stage === 'Worldforming' ? this.habitability : this.life;
  }

  meterLabel() {
    return describeMeasure(this.meterValue(), this.stage);
  }

  applyEffects(effects, factor = 1) {
    for (const variable of VARIABLES) {
      const nextValue = this.variables[variable] + (effects[variable] ?? 0) * factor;
      this.variables[variable] = clamp(nextValue, -30, 30);
    }
  }

  derivedBiases() {
    const values = this.variables;
    return {
      aquatic: values.Oceans * 1.2 + values.Moisture * 0.7 + values.Diversity * 0.35 - values.Upheaval * 0.25,
      terrestrial: values.Fertility * 1.1 + values.Warmth * 0.55 - values.Oceans * 0.35 - values.Tempest * 0.2,
      aerial: values.Tempest * 0.95 + values.Warmth * 0.45 + values.Ingenuity * 0.2 - values.Oceans * 0.15,
      subterranean: values.Upheaval * 1.05 + values.Dominance * 0.25 + values.Fertility * 0.3 - values.Moisture * 0.25,
      Cooperation: values.Diversity * 0.9 + values.Fertility * 0.25 - values.Dominance * 0.65 - values.Tempest * 0.15,
      Aggression: values.Dominance * 0.9 + values.Tempest * 0.5 + values.Upheaval * 0.4 - values.Moisture * 0.15,
      Adaptability: values.Diversity * 0.7 + values.Ingenuity * 0.7 + values.Moisture * 0.2 - values.Dominance * 0.15,
      Curiosity: values.Ingenuity * 0.95 + values.Warmth * 0.25 + values.Oceans * 0.2 - values.Tempest * 0.1,
      Resilience: values.Upheaval * 0.45 + values.Tempest * 0.35 + values.Fertility * 0.35 + values.Diversity * 0.35,
    };
  }

  visibleSigns() {
    const ranked = Object.entries(this.variables).sort((left, right) => Math.abs(right[1]) - Math.abs(left[1]));
    const lines = [visibleStageSigns[this.stage]];
    for (const [variable, value] of ranked) {
      if (Math.abs(value) < 6) continue;
      lines.push(value >= 0 ? positiveSigns[variable] : negativeSigns[variable]);
      if (lines.length === 3) break;
    }
    while (lines.length < 3) {
      if (this.stage === 'Worldforming') lines.push('The sky waits for its final temper.');
      else if (this.dominantSpecies) lines.push(`${this.dominantSpecies.name} carries the age forward.`);
      else lines.push('Life stays close to shelter and persists.');
    }
    return lines;
  }

  supportScore() {
    const values = this.variables;
    const warmthBalance = Math.max(0, 12 - Math.abs(values.Warmth - 3));
    const moistureBalance = Math.max(0, 12 - Math.abs(values.Moisture));
    if (this.stage === 'Worldforming') {
      const oceansBalance = Math.max(0, 12 - Math.abs(values.Oceans));
      return warmthBalance + moistureBalance + oceansBalance + values.Fertility * 0.55 - Math.abs(values.Tempest) * 0.6 - Math.abs(values.Upheaval) * 0.45;
    }
    return values.Diversity * 0.42 + values.Fertility * 0.48 + warmthBalance * 0.85 + moistureBalance * 0.85 + values.Oceans * 0.12 - Math.abs(values.Tempest) * 0.52 - Math.abs(values.Upheaval) * 0.46 - Math.max(0, values.Dominance - values.Diversity) * 0.85;
  }

  civilizationPressure() {
    if (!this.civilization) return 0;
    return 0.65 + this.collapseMarks * 0.4 + (this.stage === 'Ruin or Renewal' ? 0.5 : 0.15);
  }

  updateMeter(delta) {
    if (this.stage === 'Worldforming') {
      this.habitability = clamp(this.habitability + delta, 8, 100);
      return;
    }
    this.life = clamp(this.life + delta, 0, 100);
  }

  ensureGuaranteedSurvival() {
    if (this.stage === 'First Life' && this.life < 18) {
      this.life = 18;
      return;
    }
    if (this.stage === 'Complex Life' && this.stageTurn < this.stageGoal && this.life < 16) {
      this.life = 16;
    }
  }

  crisisActive() {
    return this.stage !== 'Worldforming' && this.life < 26;
  }

  updateCrisisFlag() {
    const active = this.crisisActive();
    const recovered = this.inCrisis && this.life >= 38;
    this.inCrisis = active;
    if (recovered) this.recoveries += 1;
    return recovered;
  }

  visualState() {
    const values = this.variables;
    return {
      warmth: clamp((values.Warmth + 30) / 60, 0, 1),
      moisture: clamp((values.Moisture + 30) / 60, 0, 1),
      tempest: clamp(Math.abs(values.Tempest) / 24, 0, 1),
      upheaval: clamp(Math.abs(values.Upheaval) / 24, 0, 1),
      oceans: clamp((values.Oceans + 30) / 60, 0, 1),
      fertility: clamp((values.Fertility + 30) / 60, 0, 1),
      diversity: clamp((values.Diversity + 30) / 60, 0, 1),
      ingenuity: clamp((values.Ingenuity + 30) / 60, 0, 1),
      dominance: clamp((values.Dominance + 30) / 60, 0, 1),
      entropy: clamp(this.entropy / 26, 0, 1),
      stageIndex: this.stageIndex() / (STAGE_ORDER.length - 1),
      hasCivilization: Boolean(this.civilization),
    };
  }
}
export class DecisionGenerator {
  constructor(rng) {
    this.rng = rng;
  }

  generate(state) {
    const compatible = DECISION_TEMPLATES.filter((template) => template.stages.includes(state.stage));
    const candidates = [];
    const seen = new Set();
    const target = randomInt(this.rng, 12, 15);

    while (candidates.length < target && compatible.length > 0) {
      const category = this.pickCategory(state);
      const pool = compatible.filter((template) => template.category === category);
      const template = pick(this.rng, pool.length ? pool : compatible);
      const severity = pick(this.rng, SEVERITIES);
      const variant = pick(this.rng, template.titleVariants);
      const key = `${template.id}-${severity.key}-${variant}`;
      if (seen.has(key)) continue;
      seen.add(key);
      candidates.push(this.buildOption(state, template, severity, variant));
    }

    const used = new Set();
    return ['stabilizing', 'destabilizing', 'ambiguous'].map((category) => {
      const choice = this.selectByCategory(state, candidates, category, used) ?? this.selectByCategory(state, candidates, category);
      if (choice) used.add(choice.id);
      return choice;
    }).filter(Boolean);
  }

  pickCategory(state) {
    const weights = state.crisisActive() ? [6, 2, 5] : [4, 4, 4];
    const total = weights.reduce((sum, value) => sum + value, 0);
    const roll = this.rng() * total;
    if (roll < weights[0]) return 'stabilizing';
    if (roll < weights[0] + weights[1]) return 'destabilizing';
    return 'ambiguous';
  }

  buildOption(state, template, severity, variant) {
    const immediate = Object.fromEntries(
      Object.entries(template.effects).map(([variable, value]) => [variable, Math.round(value * severity.factor)])
    );
    const delayed = template.delayed.map((item) => ({
      turn: state.turn + randomInt(this.rng, item.delay[0], item.delay[1]),
      effects: Object.fromEntries(
        Object.entries(item.effects).map(([variable, value]) => [variable, Math.round(value * severity.factor)])
      ),
      text: item.text,
    }));
    return {
      id: `${template.id}-${severity.key}-${variant}`,
      title: `${severity.label} ${variant}`,
      subtitle: template.subtitle,
      category: template.category,
      domain: template.domain,
      severity: severity.label,
      immediate,
      delayed,
      poetry: template.poetry,
      effectHint: describeDecisionEffects(immediate),
    };
  }

  selectByCategory(state, candidates, category, used = new Set()) {
    const pool = candidates.filter((candidate) => candidate.category === category && !used.has(candidate.id));
    const fallbackPool = candidates.filter((candidate) => !used.has(candidate.id));
    const source = pool.length ? pool : fallbackPool;
    if (!source.length) return null;
    const ranked = [...source].sort((left, right) => this.score(state, right) - this.score(state, left));
    return pick(this.rng, ranked.slice(0, Math.min(3, ranked.length)));
  }

  score(state, option) {
    const ranked = strongestEffects(option.immediate);
    const totalShift = ranked.reduce((sum, [, value]) => sum + Math.abs(value), 0);
    if (option.category === 'stabilizing') {
      return totalShift + Math.max(0, option.immediate.Moisture) + Math.max(0, option.immediate.Fertility) + Math.max(0, -option.immediate.Tempest) + Math.max(0, -option.immediate.Upheaval) + (state.crisisActive() ? 4 : 0);
    }
    if (option.category === 'destabilizing') {
      return totalShift + Math.max(0, option.immediate.Upheaval) + Math.max(0, option.immediate.Tempest);
    }
    return totalShift + Math.max(0, option.immediate.Diversity) + Math.max(0, option.immediate.Ingenuity);
  }
}

export class SpeciesSystem {
  constructor(rng) {
    this.rng = rng;
  }

  weightedLineage(habitat) {
    const weights = {
      aquatic: [['fish', 4], ['shark', 3], ['bird', 1], ['primate', 1], ['bug', 1]],
      amphibious: [['fish', 2], ['bird', 2], ['bug', 2], ['primate', 2], ['grazer', 1], ['shark', 1]],
      terrestrial: [['grazer', 3], ['primate', 2], ['reptile', 2], ['sloth', 2], ['bird', 1], ['bug', 1], ['shark', 1]],
      aerial: [['bird', 4], ['bug', 3], ['fish', 1], ['shark', 1]],
      subterranean: [['bug', 5], ['reptile', 2], ['grazer', 2], ['primate', 1], ['fish', 1]],
    };
    const pool = weights[habitat] ?? weights.terrestrial;
    const total = pool.reduce((sum, [, weight]) => sum + weight, 0);
    let roll = this.rng() * total;
    for (const [lineage, weight] of pool) {
      roll -= weight;
      if (roll <= 0) return lineage;
    }
    return pool[pool.length - 1][0];
  }

  pickLineage(habitat, previous) {
    if (previous?.lineage && this.rng() < 0.68) return previous.lineage;
    return this.weightedLineage(habitat);
  }

  composeName(lineage, habitat, previous, fallbackNames) {
    if (this.rng() < 0.42) return pick(this.rng, fallbackNames);
    const prefix = pick(this.rng, habitatPrefixes[habitat]);
    const nounPool = lineageNouns[lineage];
    const inheritedNoun = previous?.lineage === lineage ? previous.name.split(' ').slice(-1)[0] : null;
    const noun = inheritedNoun && this.rng() < 0.55 ? inheritedNoun : pick(this.rng, nounPool);
    return `${prefix} ${noun}`;
  }

  describeLineage(lineage, habitat, behaviorKeys, collective) {
    if (lineage === 'fish' && habitat === 'aerial') return 'Born of fish. It has taken to the high air.';
    if (lineage === 'bird' && habitat === 'aquatic') return 'Born of birds. It has entered the open water like a whale.';
    if (lineage === 'shark' && habitat === 'terrestrial') return 'Born of sharks. It now walks on land.';
    if (lineage === 'primate' && habitat === 'aquatic') return 'Born of primates. It lives its full life in water.';
    if (lineage === 'grazer' && behaviorKeys.includes('Aggression')) return 'Born of grazers. Its old grazing mouth now seeks flesh.';
    if (lineage === 'grazer' && collective) return 'The herd has bent toward one mind.';
    if (lineage === 'bug' && habitat === 'aquatic') return 'Born of bugs. It has entered the water without surrendering the swarm.';
    if (lineage === 'bird' && habitat === 'subterranean') return 'Born of birds. It nests now in root dark and stone.';
    if (lineage === 'fish' && habitat === 'terrestrial') return 'Born of fish. It has learned the long weight of land.';
    if (naturalLineageHabitats[lineage] !== habitat) return `Born of ${lineageOrigins[lineage]}. It has learned the way of ${habitat.replace('subterranean', 'the underworld')}.`;
    return null;
  }

  generate(state, previous = null) {
    const biases = state.derivedBiases();
    const habitat = this.pickHabitat(biases);
    const behaviorKeys = ['Cooperation', 'Aggression', 'Adaptability', 'Curiosity', 'Resilience']
      .sort((left, right) => biases[right] - biases[left])
      .slice(0, 2);
    const names = SPECIES_POOLS.habitats[habitat];
    const lineage = this.pickLineage(habitat, previous);
    const bugCandidates = names.filter((candidate) => bugPattern.test(candidate));
    const bugBias = lineage === 'bug' || behaviorKeys.includes('Cooperation') || biases.subterranean > 6 || biases.aerial > 8;
    const fallbackPool = bugCandidates.length && bugBias && this.rng() < 0.72 ? bugCandidates : names;
    let name = this.composeName(lineage, habitat, previous, fallbackPool);
    if (previous && this.rng() < 0.34) {
      const carry = previous.name.split(' ')[0];
      const rest = name.split(' ').slice(1).join(' ');
      name = rest ? `${carry} ${rest}` : name;
    }
    const behaviors = behaviorKeys.map((key) => pick(this.rng, SPECIES_POOLS.behaviors[key]));
    const mindful = state.stage === 'Thinking Beasts' || state.stage === 'Civilization' || state.stage === 'Ruin or Renewal';
    const toolCapable = mindful && state.mindEchoes >= 1 && biases.Curiosity > 7;
    const bugLike = lineage === 'bug' || bugPattern.test(name);
    const collective = bugLike
      ? behaviorKeys.includes('Cooperation') || biases.Curiosity > 5 || biases.Adaptability > 6
      : behaviorKeys.includes('Cooperation') && (biases.Curiosity > 6 || biases.Adaptability > 6);
    const summaryParts = [
      `${name}.`,
      `${behaviors[0]} and ${behaviors[1]}.`,
      habitatDescriptions[habitat],
    ];
    const lineageLine = this.describeLineage(lineage, habitat, behaviorKeys, collective);
    if (lineageLine) summaryParts.push(lineageLine);
    if (bugLike) summaryParts.push('Small bodies move in ruthless number.');
    if (collective) summaryParts.push('Many minds lean toward one command.');
    if (toolCapable) {
      summaryParts.push('It experiments with objects and repeated methods.');
    }
    return {
      name,
      lineage,
      habitat,
      behaviors: behaviorKeys,
      mindful,
      toolCapable,
      bugLike,
      collective,
      summary: summaryParts.join(' '),
    };
  }

  pickHabitat(biases) {
    const habitatScores = {
      aquatic: biases.aquatic,
      terrestrial: biases.terrestrial,
      aerial: biases.aerial,
      subterranean: biases.subterranean,
    };
    const ranked = Object.entries(habitatScores).sort((left, right) => right[1] - left[1]);
    if (['aquatic', 'terrestrial'].includes(ranked[0][0]) && Math.abs(ranked[0][1] - ranked[1][1]) < 4.5) {
      return 'amphibious';
    }
    return ranked[0][0];
  }
}
export class CivilizationSystem {
  constructor(rng) {
    this.rng = rng;
  }

  civRoot(species) {
    const parts = species.name.split(' ');
    if (species.bugLike && parts.length > 1) return parts[parts.length - 1];
    return parts[0];
  }

  collectiveFocus(state, biases) {
    if (biases.Curiosity > 8 || state.variables.Ingenuity > 8) {
      return 'It shares thought through scent, rhythm, and omen.';
    }
    return 'Many bodies carry one command.';
  }

  process(state, history) {
    const lines = [];
    if (!state.civilization && this.shouldEmerge(state)) {
      state.civilization = this.createCivilization(state);
      history.add(state.year, state.turn, 'civilization', `${state.civilization.name} rises from ${state.dominantSpecies.name}.`);
      lines.push(`${state.civilization.name} rises from ${state.dominantSpecies.name}.`);
    }
    if (!state.civilization) return lines;

    if (!state.civilization.bugLike
      && state.dominantSpecies?.bugLike
      && state.dominantSpecies.collective
      && ['Civilization', 'Ruin or Renewal'].includes(state.stage)) {
      const biases = state.derivedBiases();
      state.civilization.bugLike = true;
      state.civilization.collective = true;
      state.civilization.name = `${this.civRoot(state.dominantSpecies)} ${pick(this.rng, SWARM_SUFFIXES)}`;
      state.civilization.focus = this.collectiveFocus(state, biases);
      state.civilization.summary = `${state.civilization.name}. ${state.civilization.ethos} ${state.civilization.focus}`;
      const line = `${state.civilization.name} inherits the old cities and binds them into a swarm will.`;
      history.add(state.year, state.turn, 'civilization', line);
      lines.push(line);
    }

    const event = this.selectEvent(state);
    state.applyEffects(event.effects);
    state.civilization.stability = clamp(state.civilization.stability + event.stability, 0, 100);
    state.civilization.summary = `${state.civilization.name}. ${state.civilization.ethos} ${state.civilization.focus}`;
    state.civilization.lastEvent = event.text;
    lines.push(event.text);

    if (event.kind === 'collapse') state.collapseMarks += 1;
    if (['war', 'holy-war', 'collapse', 'renewal'].includes(event.kind)) {
      history.add(state.year, state.turn, event.kind, event.text);
    }
    return lines;
  }

  shouldEmerge(state) {
    if (state.civilization || !state.dominantSpecies) return false;
    if (!['Thinking Beasts', 'Civilization', 'Ruin or Renewal'].includes(state.stage)) return false;
    const biases = state.derivedBiases();
    const socialPressure = Math.max(biases.Curiosity, biases.Cooperation, biases.Aggression);
    const collectiveBonus = state.dominantSpecies.collective ? 1 : 0;
    const readiness = state.variables.Ingenuity >= 4 - collectiveBonus || state.dominantSpecies.toolCapable || biases.Curiosity > 5 - collectiveBonus;
    return state.stageTurn >= 1 && state.life >= 18 - collectiveBonus * 2 && state.ageCount >= 3 - collectiveBonus && state.mindEchoes >= 1 && readiness && socialPressure > 5 - collectiveBonus;
  }

  createCivilization(state) {
    const biases = state.derivedBiases();
    const collective = Boolean(state.dominantSpecies.collective || state.dominantSpecies.bugLike);
    const bugLike = Boolean(state.dominantSpecies.bugLike);
    let tone = 'order';
    if (biases.Aggression > biases.Cooperation + 4) tone = 'war';
    else if (biases.Curiosity > 10) tone = 'craft';
    else if (biases.Cooperation > 8) tone = 'kin';
    else if (biases.Resilience > 8) tone = 'endure';
    const root = this.civRoot(state.dominantSpecies);
    const suffixes = bugLike ? SWARM_SUFFIXES : CIVILIZATION_SUFFIXES;
    const name = `${root} ${pick(this.rng, suffixes)}`;
    const focus = collective && bugLike
      ? this.collectiveFocus(state, biases)
      : state.variables.Oceans > 8
        ? 'Its roads are made of water.'
        : biases.Curiosity > 9
          ? 'Its hunger turns toward tools and hidden laws.'
          : state.variables.Dominance > 9
            ? 'Its gaze turns toward conquest.'
            : 'It builds storehouses, stories, and walls.';
    return {
      name,
      ethos: civEthos[tone],
      focus,
      stability: 56,
      collective,
      bugLike,
      holyWarSeen: false,
      lastEvent: `${name} raises its first shared laws.`,
      summary: `${name}. ${civEthos[tone]} ${focus}`,
    };
  }

  selectEvent(state) {
    const biases = state.derivedBiases();
    if (!state.civilization.holyWarSeen
      && state.civilization.collective
      && state.civilization.bugLike
      && state.stage !== 'Thinking Beasts'
      && state.variables.Ingenuity >= 5
      && biases.Curiosity > 5
      && (biases.Aggression > 3 || state.variables.Dominance > 4)) {
      state.civilization.holyWarSeen = true;
      return {
        kind: 'holy-war',
        stability: -8,
        text: `${state.civilization.name} fights a holy war to decide whether you are god.`,
        effects: {
          Warmth: 0, Moisture: -1, Tempest: 1, Upheaval: 2, Oceans: 0,
          Fertility: -2, Diversity: -2, Ingenuity: 1, Dominance: 3,
        },
      };
    }
    if (state.stage === 'Ruin or Renewal' && (state.entropy > 18 || state.civilization.stability < 32)) {
      return {
        kind: 'collapse',
        stability: -10,
        text: `${state.civilization.name} enters another collapse cycle.`,
        effects: {
          Warmth: 0, Moisture: -1, Tempest: 2, Upheaval: 2, Oceans: -1,
          Fertility: -3, Diversity: -3, Ingenuity: -2, Dominance: -2,
        },
      };
    }
    if (state.crisisActive() && biases.Cooperation > biases.Aggression) {
      return {
        kind: 'renewal',
        stability: 6,
        text: `${state.civilization.name} turns to repair, ration, and careful stewardship.`,
        effects: {
          Warmth: 0, Moisture: 1, Tempest: -1, Upheaval: -1, Oceans: 0,
          Fertility: 2, Diversity: 2, Ingenuity: 1, Dominance: -2,
        },
      };
    }
    if (state.variables.Dominance > 10 && state.variables.Fertility < 0) {
      return {
        kind: 'war',
        stability: -6,
        text: `${state.civilization.name} wages resource wars across thinning ground.`,
        effects: {
          Warmth: 1, Moisture: -1, Tempest: 1, Upheaval: 1, Oceans: 0,
          Fertility: -3, Diversity: -2, Ingenuity: 1, Dominance: 3,
        },
      };
    }
    if (biases.Curiosity > 10) {
      return {
        kind: 'industry',
        stability: 1,
        text: `${state.civilization.name} spreads through craft, study, and extraction.`,
        effects: {
          Warmth: 2, Moisture: 0, Tempest: 0, Upheaval: 1, Oceans: 0,
          Fertility: -2, Diversity: 0, Ingenuity: 3, Dominance: 1,
        },
      };
    }
    if (biases.Aggression > biases.Cooperation + 3) {
      return {
        kind: 'war',
        stability: -4,
        text: `${state.civilization.name} fights a war of creed and prestige.`,
        effects: {
          Warmth: 0, Moisture: 0, Tempest: 1, Upheaval: 1, Oceans: 0,
          Fertility: -1, Diversity: -2, Ingenuity: -1, Dominance: 3,
        },
      };
    }
    return {
      kind: 'trade',
      stability: 2,
      text: `${state.civilization.name} binds distant settlements through trade and custom.`,
      effects: {
        Warmth: 0, Moisture: 1, Tempest: -1, Upheaval: 0, Oceans: 2,
        Fertility: 1, Diversity: 1, Ingenuity: 2, Dominance: 0,
      },
    };
  }
}

export class EntropySystem {
  constructor(rng) {
    this.rng = rng;
  }

  advance(state) {
    let growth = STAGE_CONFIGS[state.stage].entropy + state.collapseMarks * 0.12;
    if (state.civilization) growth += 0.18 + Math.max(0, state.variables.Ingenuity) / 140;
    if (state.crisisActive()) growth += 0.14;
    state.entropy += growth;
  }

  decisionFactor(state, category) {
    if (category === 'stabilizing') return Math.max(0.42, 1 - state.entropy * 0.018);
    if (category === 'destabilizing') return 1 + state.entropy * 0.02;
    return 1 + state.entropy * 0.01;
  }

  backgroundInstability(state) {
    const pressure = Math.floor(state.entropy / 6.5);
    if (pressure <= 0) return [];
    const effects = {
      Warmth: randomInt(this.rng, 0, 1),
      Moisture: randomInt(this.rng, -1, 1),
      Tempest: randomInt(this.rng, 0, pressure),
      Upheaval: randomInt(this.rng, 0, pressure),
      Oceans: randomInt(this.rng, -1, 1),
      Fertility: -randomInt(this.rng, 0, Math.max(1, Math.floor(pressure / 2))),
      Diversity: -randomInt(this.rng, 0, Math.max(1, Math.floor(pressure / 2))),
      Ingenuity: 0,
      Dominance: randomInt(this.rng, 0, Math.max(1, Math.floor(pressure / 2))),
    };
    state.applyEffects(effects);
    return state.entropy >= 12 ? ['Old instabilities gather strength.'] : [];
  }

  applyMeterDrift(state) {
    const support = state.supportScore();
    if (state.stage === 'Worldforming') {
      const delta = Math.round(support / 9 - state.entropy * 0.45);
      state.updateMeter(delta);
      return delta;
    }
    const earlyMercy = state.stage === 'First Life' ? 2 : state.stage === 'Complex Life' ? 1 : 0;
    let delta = Math.round(support / 10 + earlyMercy - state.entropy * (0.18 + state.stageIndex() * 0.05) - state.civilizationPressure());
    if (state.stage === 'Civilization') delta -= 1;
    if (state.stage === 'Ruin or Renewal') delta -= 2;
    state.updateMeter(delta);
    return delta;
  }
}

export class AgeSystem {
  constructor(rng, speciesSystem) {
    this.rng = rng;
    this.speciesSystem = speciesSystem;
  }

  process(state, history) {
    const qualified = Object.entries(state.variables)
      .filter(([, value]) => Math.abs(value) >= 20)
      .sort((left, right) => Math.abs(right[1]) - Math.abs(left[1]));
    if (qualified.length < 3) return [];

    const drivers = qualified.slice(0, 3);
    const constraints = Object.entries(state.variables).sort((left, right) => left[1] - right[1]).slice(0, 2);
    const prefix = pick(this.rng, agePrefixes[state.stage]);
    const [firstKey, firstValue] = drivers[0];
    const [secondKey, secondValue] = drivers[1];
    const firstWord = ageWords[firstKey][firstValue >= 0 ? 0 : 1];
    const secondWord = constraints[0][1] < 0 ? ageWords[constraints[0][0]][1] : ageWords[secondKey][secondValue >= 0 ? 0 : 1];
    state.currentAge = `The ${prefix} Age of ${firstWord} and ${secondWord}`;
    state.ageCount += 1;

    for (const [variable] of drivers) {
      if (variable === 'Ingenuity') state.mindEchoes += 1;
      state.variables[variable] = 0;
    }

    history.add(state.year, state.turn, 'age', `${state.currentAge} begins.`);
    const lines = [`${state.currentAge} begins.`];

    if (state.stage !== 'Worldforming') {
      state.dominantSpecies = this.speciesSystem.generate(state, state.dominantSpecies);
      history.add(state.year, state.turn, 'species', `${state.dominantSpecies.name} rises to dominance.`);
      lines.push(`${state.dominantSpecies.name} rises to dominance.`);
    }
    return lines;
  }
}

export class StageManager {
  constructor(rng, speciesSystem) {
    this.rng = rng;
    this.speciesSystem = speciesSystem;
  }

  process(state, history) {
    const lines = [];
    if (state.stage === 'Worldforming' && state.stageTurn >= state.stageGoal) {
      state.worldOrigin = stageOriginDescription(state.variables);
      state.setStage('First Life');
      state.habitability = Math.max(state.habitability, 68);
      state.life = 62;
      state.currentAge = 'The First Quiet';
      state.dominantSpecies = this.speciesSystem.generate(state);
      history.add(state.year, state.turn, 'stage', state.worldOrigin);
      history.add(state.year, state.turn, 'stage', 'First life takes hold.');
      history.add(state.year, state.turn, 'species', `${state.dominantSpecies.name} becomes the first dominant lineage.`);
      lines.push(state.worldOrigin, 'First life takes hold.');
      return lines;
    }
    if (state.stage === 'First Life' && state.stageTurn >= state.stageGoal) {
      state.setStage('Complex Life');
      state.life = Math.max(state.life, 58);
      state.currentAge = 'The Age of Many Shapes';
      state.dominantSpecies = this.speciesSystem.generate(state, state.dominantSpecies);
      history.add(state.year, state.turn, 'stage', 'Complex life claims the world.');
      history.add(state.year, state.turn, 'species', `${state.dominantSpecies.name} leads the new abundance.`);
      lines.push('Bodies grow stranger and more capable.', 'Complex life claims the world.');
      return lines;
    }
    if (state.stage === 'Complex Life' && state.stageTurn >= state.stageGoal) {
      const biases = state.derivedBiases();
      const readyForGiants = state.life >= 30 && state.ageCount >= 2 && (state.variables.Diversity > 3 || biases.Adaptability > 5);
      const overdueAscent = state.stageTurn >= state.stageGoal + 5 && state.ageCount >= 1 && (state.variables.Diversity > 0 || biases.Resilience > 4);
      if (readyForGiants || overdueAscent) {
        state.setStage('Great Creatures');
        state.life = Math.max(state.life, 42);
        state.dominantSpecies = this.speciesSystem.generate(state, state.dominantSpecies);
        history.add(state.year, state.turn, 'stage', 'Great creatures rise from the swarm of forms.');
        history.add(state.year, state.turn, 'species', `${state.dominantSpecies.name} now commands the age.`);
        lines.push('Great creatures rise from the swarm of forms.');
      }
    } else if (state.stage === 'Great Creatures' && state.stageTurn >= state.stageGoal) {
      const biases = state.derivedBiases();
      const readyForThought = state.life >= 26 && state.ageCount >= 3 && (state.mindEchoes >= 1 || state.variables.Ingenuity >= 8) && biases.Curiosity > 4;
      const overdueAwakening = state.stageTurn >= state.stageGoal + 4 && state.ageCount >= 2 && biases.Curiosity > 3;
      if (readyForThought || overdueAwakening) {
        state.setStage('Thinking Beasts');
        state.life = Math.max(state.life, 36);
        state.dominantSpecies = this.speciesSystem.generate(state, state.dominantSpecies);
        history.add(state.year, state.turn, 'stage', 'Thinking beasts awaken.');
        lines.push('A dominant beast begins to study cause and consequence.');
      }
    } else if (state.stage === 'Thinking Beasts' && state.civilization && state.stageTurn >= 2) {
      state.setStage('Civilization');
      state.life = Math.max(state.life, 32);
      history.add(state.year, state.turn, 'stage', 'Cities and laws begin to spread.');
      lines.push('Cities and laws begin to spread.');
    } else if (state.stage === 'Civilization') {
      if (state.entropy >= 18 || state.collapseMarks >= 1 || state.life < 44) {
        state.setStage('Ruin or Renewal');
        history.add(state.year, state.turn, 'stage', 'The age turns toward ruin or renewal.');
        lines.push('The age turns toward ruin or renewal.');
      }
    }
    return lines;
  }
}
export class GameLoop {
  constructor(seed = Math.floor(Date.now() % 2147483647)) {
    this.seed = seed;
    this.rng = createRng(seed);
    this.history = new HistoryLog();
    this.state = new PlanetState(this.rng);
    this.history.add(0, 0, 'stage', 'Stone waits beneath a patient sun.');
    this.delayedQueue = new DelayedEffectQueue();
    this.speciesSystem = new SpeciesSystem(this.rng);
    this.decisionGenerator = new DecisionGenerator(this.rng);
    this.civilizationSystem = new CivilizationSystem(this.rng);
    this.entropySystem = new EntropySystem(this.rng);
    this.ageSystem = new AgeSystem(this.rng, this.speciesSystem);
    this.stageManager = new StageManager(this.rng, this.speciesSystem);
    this.currentChoices = this.decisionGenerator.generate(this.state);
  }

  choose(optionId) {
    if (this.state.extinct) return this.viewModel();

    const option = this.currentChoices.find((choice) => choice.id === optionId) ?? this.currentChoices[0];
    this.state.advanceClock();
    this.entropySystem.advance(this.state);
    const lines = this.applyChoice(option);

    const delayed = this.delayedQueue.resolve(this.state.turn);
    for (const item of delayed) {
      this.state.applyEffects(item.effects);
      lines.push(item.text);
    }

    lines.push(...this.civilizationSystem.process(this.state, this.history));
    lines.push(...this.entropySystem.backgroundInstability(this.state));
    const drift = this.entropySystem.applyMeterDrift(this.state);
    lines.push(this.describeDrift(drift));
    lines.push(...this.ageSystem.process(this.state, this.history));
    lines.push(...this.stageManager.process(this.state, this.history));

    if (this.state.updateCrisisFlag()) {
      this.history.add(this.state.year, this.state.turn, 'recovery', 'Life recovers from the brink.');
      lines.push('Life gathers itself and refuses the grave.');
    }

    this.state.ensureGuaranteedSurvival();
    if (this.state.stage !== 'Worldforming' && this.state.life <= 0) {
      this.state.extinct = true;
      const line = pick(this.rng, FINAL_LINES);
      const subject = this.state.civilization
        ? `${this.state.civilization.name} is gone.`
        : this.state.dominantSpecies
          ? `${this.state.dominantSpecies.name} has fallen.`
          : 'Life has ended.';
      this.state.finalText = `${subject} ${line}`;
      this.history.add(this.state.year, this.state.turn, 'extinction', this.state.finalText);
      lines.push(this.state.finalText);
    }

    this.state.recentConsequences = lines.slice(-5);
    this.currentChoices = this.state.extinct ? [] : this.decisionGenerator.generate(this.state);
    return this.viewModel();
  }

  applyChoice(option) {
    const factor = this.entropySystem.decisionFactor(this.state, option.category);
    this.state.applyEffects(option.immediate, factor);
    this.delayedQueue.addMany(option.delayed);
    return [
      `${option.title} is chosen.`,
      option.category === 'stabilizing'
        ? 'Order is invited in. The cost remains.'
        : option.category === 'destabilizing'
          ? 'Power is taken through upheaval.'
          : 'A gift and a wound arrive together.',
    ];
  }

  describeDrift(drift) {
    if (drift >= 4) return 'The world answers with strength.';
    if (drift >= 1) return 'The climate yields a season of relief.';
    if (drift >= -2) return 'The gain is real. The strain remains.';
    if (drift >= -5) return 'The price is felt at once.';
    return 'The wound opens wider.';
  }

  viewModel() {
    return {
      seed: this.seed,
      turn: this.state.turn,
      year: this.state.year,
      stage: this.state.stage,
      age: this.state.currentAge,
      meterName: this.state.meterName(),
      meterValue: this.state.meterValue(),
      meterLabel: this.state.meterLabel(),
      stageProgress: Math.round((this.state.stageTurn / this.state.stageGoal) * 100),
      stageGoal: this.state.stageGoal,
      stageTurn: this.state.stageTurn,
      worldOrigin: this.state.worldOrigin,
      worldSigns: this.state.visibleSigns(),
      species: this.state.dominantSpecies,
      civilization: this.state.civilization,
      recentConsequences: this.state.recentConsequences,
      history: this.history.recent(),
      choices: this.currentChoices,
      gameOver: this.state.extinct,
      finalText: this.state.finalText,
      visualState: this.state.visualState(),
      ageCount: this.state.ageCount,
      mindEchoes: this.state.mindEchoes,
      rulesNote: 'You shape climate, oceans, stone, and sky. Life answers on its own.',
    };
  }
}
