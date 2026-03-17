const formatYear = (year) => year.toLocaleString('en-US');

function meterPercent(value) {
  return `${Math.max(0, Math.min(100, value))}%`;
}

function renderList(container, items, renderer) {
  container.innerHTML = '';
  items.forEach((item) => container.appendChild(renderer(item)));
}

export class PlanetUI {
  constructor(root, { onChoice, onRestart }) {
    this.root = root;
    this.onChoice = onChoice;
    this.onRestart = onRestart;

    this.turnValue = root.querySelector('#turn-value');
    this.yearValue = root.querySelector('#year-value');
    this.stageValue = root.querySelector('#stage-value');
    this.ageValue = root.querySelector('#age-value');
    this.worldOrigin = root.querySelector('#world-origin');
    this.meterTitle = root.querySelector('#meter-title');
    this.meterFill = root.querySelector('#meter-fill');
    this.meterValue = root.querySelector('#meter-value');
    this.meterLabel = root.querySelector('#meter-label');
    this.stageProgressFill = root.querySelector('#stage-progress-fill');
    this.stageProgressLabel = root.querySelector('#stage-progress-label');
    this.rulesNote = root.querySelector('#rules-note');
    this.worldSigns = root.querySelector('#world-signs');
    this.consequences = root.querySelector('#consequences');
    this.speciesName = root.querySelector('#species-name');
    this.speciesSummary = root.querySelector('#species-summary');
    this.civName = root.querySelector('#civ-name');
    this.civSummary = root.querySelector('#civ-summary');
    this.historyList = root.querySelector('#history-list');
    this.choices = root.querySelector('#choices');
    this.scene = root.querySelector('#scene-root');
    this.endOverlay = root.querySelector('#end-overlay');
    this.endTitle = root.querySelector('#end-title');
    this.endText = root.querySelector('#end-text');
    this.endScore = root.querySelector('#end-score');
    root.querySelector('#restart-button').addEventListener('click', () => this.onRestart());
    root.querySelector('#restart-overlay-button').addEventListener('click', () => this.onRestart());
  }

  render(model) {
    this.turnValue.textContent = model.turn;
    this.yearValue.textContent = formatYear(model.year);
    this.stageValue.textContent = model.stage;
    this.ageValue.textContent = model.age;
    this.worldOrigin.textContent = model.worldOrigin;
    this.meterTitle.textContent = model.meterName;
    this.meterFill.style.width = meterPercent(model.meterValue);
    this.meterValue.textContent = model.meterValue;
    this.meterLabel.textContent = model.meterLabel;
    this.stageProgressFill.style.width = `${model.stageProgress}%`;
    this.stageProgressLabel.textContent = `${model.stageTurn} / ${model.stageGoal} stage turns`;
    this.rulesNote.textContent = model.rulesNote;

    renderList(this.worldSigns, model.worldSigns, (line) => {
      const card = document.createElement('article');
      card.className = 'sign-card';
      card.textContent = line;
      return card;
    });

    renderList(this.consequences, model.recentConsequences, (line) => {
      const item = document.createElement('li');
      item.textContent = line;
      return item;
    });

    if (model.species) {
      this.speciesName.textContent = model.species.name;
      this.speciesSummary.textContent = model.species.summary;
    } else {
      this.speciesName.textContent = 'No dominant species yet';
      this.speciesSummary.textContent = 'The cradle is still being made.';
    }

    if (model.civilization) {
      this.civName.textContent = model.civilization.name;
      this.civSummary.textContent = model.civilization.summary;
    } else {
      this.civName.textContent = 'No civilization';
      this.civSummary.textContent = 'No city has found its voice.';
    }

    renderList(this.historyList, model.history, (entry) => {
      const item = document.createElement('li');
      item.className = 'timeline-item';
      item.innerHTML = `<span class="timeline-year">${formatYear(entry.year)}</span><span class="timeline-text">${entry.text}</span>`;
      return item;
    });

    renderList(this.choices, model.choices, (choice) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = `choice-card choice-card--${choice.category}`;
      button.innerHTML = `
        <div class="choice-card__meta">
          <span>${choice.domain}</span>
          <span>${choice.severity}</span>
        </div>
        <h3>${choice.title}</h3>
        <p class="choice-card__subtitle">${choice.subtitle}</p>
        <p class="choice-card__hint">${choice.effectHint}</p>
        <ul class="choice-card__poetry">
          ${choice.poetry.map((line) => `<li>${line}</li>`).join('')}
        </ul>
      `;
      button.addEventListener('click', () => this.onChoice(choice.id));
      return button;
    });

    this.root.dataset.stage = model.stage;
    this.applyVisualState(model.visualState);
    this.endOverlay.hidden = !model.gameOver;
    if (model.gameOver) {
      this.endTitle.textContent = 'The world falls silent';
      this.endText.textContent = model.finalText;
      this.endScore.textContent = `Turns survived: ${model.turn}`;
    }
  }

  applyVisualState(state) {
    this.scene.style.setProperty('--warmth', state.warmth.toFixed(3));
    this.scene.style.setProperty('--moisture', state.moisture.toFixed(3));
    this.scene.style.setProperty('--tempest', state.tempest.toFixed(3));
    this.scene.style.setProperty('--upheaval', state.upheaval.toFixed(3));
    this.scene.style.setProperty('--oceans', state.oceans.toFixed(3));
    this.scene.style.setProperty('--fertility', state.fertility.toFixed(3));
    this.scene.style.setProperty('--diversity', state.diversity.toFixed(3));
    this.scene.style.setProperty('--ingenuity', state.ingenuity.toFixed(3));
    this.scene.style.setProperty('--dominance', state.dominance.toFixed(3));
    this.scene.style.setProperty('--entropy', state.entropy.toFixed(3));
    this.scene.style.setProperty('--stage-depth', state.stageIndex.toFixed(3));
    this.scene.dataset.civilization = state.hasCivilization ? 'yes' : 'no';
  }
}
