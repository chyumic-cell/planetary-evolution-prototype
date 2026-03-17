import { GameLoop } from './engine.js';
import { PlanetUI } from './ui.js';

let game;

function scoreSwarmChoice(model, choice) {
  const effects = choice.immediate ?? {};
  const lifeEmergency = model.meterValue < 42 ? 10 : 0;
  const earlyGuard = ['Worldforming', 'First Life', 'Complex Life'].includes(model.stage) ? 3 : 0;
  return (effects.Upheaval ?? 0) * 2.3
    + (effects.Ingenuity ?? 0) * 3
    + (effects.Diversity ?? 0) * 1.2
    + (effects.Fertility ?? 0) * 1.4
    + (effects.Dominance ?? 0) * 0.9
    - Math.max(0, (effects.Tempest ?? 0) - 1) * 1.5
    + (choice.category === 'stabilizing' ? lifeEmergency + earlyGuard : 0)
    + ((effects.Moisture ?? 0) > 0 ? 0.8 : 0);
}

function pickAutoplayChoice(model, index, mode) {
  if (!model.choices.length) return null;
  if (mode === 'risk') return model.choices[2] ?? model.choices[model.choices.length - 1];
  if (mode === 'stability') return model.choices[0];
  if (mode === 'swarm') {
    return [...model.choices].sort((left, right) => scoreSwarmChoice(model, right) - scoreSwarmChoice(model, left))[0];
  }
  return model.choices[index % model.choices.length];
}

const ui = new PlanetUI(document.body, {
  onChoice: (choiceId) => {
    const model = game.choose(choiceId);
    ui.render(model);
    window.__planetGame = { game, model };
  },
  onRestart: () => {
    const seed = Number.parseInt(new URL(window.location.href).searchParams.get('seed') ?? '', 10);
    game = Number.isFinite(seed) ? new GameLoop(seed) : new GameLoop();
    const model = game.viewModel();
    ui.render(model);
    window.__planetGame = { game, model };
  },
});

function boot() {
  const params = new URL(window.location.href).searchParams;
  const seed = Number.parseInt(params.get('seed') ?? '', 10);
  const autoplayTurns = Number.parseInt(params.get('autoplay') ?? '', 10);
  const autoplayMode = params.get('mode') ?? 'cycle';
  game = Number.isFinite(seed) ? new GameLoop(seed) : new GameLoop();

  let model = game.viewModel();
  ui.render(model);

  if (Number.isFinite(autoplayTurns) && autoplayTurns > 0) {
    for (let index = 0; index < autoplayTurns; index += 1) {
      if (model.gameOver) break;
      const choice = pickAutoplayChoice(model, index, autoplayMode);
      if (!choice) break;
      model = game.choose(choice.id);
    }
    ui.render(model);
  }

  window.__planetGame = { game, model };
}

try {
  boot();
} catch (error) {
  console.error(error);
  const crash = document.createElement('pre');
  crash.id = 'boot-error';
  crash.textContent = error.stack ?? error.message;
  crash.style.whiteSpace = 'pre-wrap';
  crash.style.padding = '16px';
  crash.style.margin = '16px';
  crash.style.borderRadius = '16px';
  crash.style.background = 'rgba(90, 20, 20, 0.9)';
  crash.style.color = '#fff';
  document.body.prepend(crash);
}
