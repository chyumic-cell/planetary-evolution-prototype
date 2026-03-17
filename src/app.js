import { GameLoop } from './engine.js';
import { PlanetUI } from './ui.js';

let game;

function pickAutoplayChoice(model, index, mode) {
  if (!model.choices.length) return null;
  if (mode === 'risk') return model.choices[2] ?? model.choices[model.choices.length - 1];
  if (mode === 'stability') return model.choices[0];
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

boot();
