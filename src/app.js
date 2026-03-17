import { GameLoop } from './engine.js';
import { PlanetUI } from './ui.js';

let game = new GameLoop();

const ui = new PlanetUI(document.body, {
  onChoice: (choiceId) => {
    ui.render(game.choose(choiceId));
  },
  onRestart: () => {
    game = new GameLoop();
    ui.render(game.viewModel());
  },
});

ui.render(game.viewModel());
