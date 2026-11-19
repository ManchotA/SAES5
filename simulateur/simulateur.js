// Simulateur du boîtier : 10 touches avec LED, reliées au back par le WebSocket /ws/boitier.
// Le format des messages est décrit dans docs/contrats.md (§5).

const NB_BOUTONS = 10;
const ETEINTE = [0, 0, 0];
const DELAI_RECONNEXION = 2000;
const TAILLE_JOURNAL = 30;

const boitier = document.getElementById('boitier');
const grille = document.getElementById('touches');
const etat = document.getElementById('etat');
const journal = document.getElementById('journal');

const touches = [];
const minuteries = [];
let couleurs = Array.from({ length: NB_BOUTONS }, () => ETEINTE);
let lien = null;
let connecte = false;

// --- Touches ---

for (let bouton = 1; bouton <= NB_BOUTONS; bouton++) {
  const touche = document.createElement('button');
  touche.type = 'button';
  touche.className = 'touche';
  touche.innerHTML = `<span class="numero">K${bouton}</span><span class="clavier">${bouton % 10}</span>`;
  touche.addEventListener('pointerdown', () => appuyer(bouton));
  grille.append(touche);
  touches.push(touche);
}

document.addEventListener('keydown', (e) => {
  if (e.repeat || e.ctrlKey || e.altKey || e.metaKey || !/^[0-9]$/.test(e.key)) return;
  appuyer(e.key === '0' ? 10 : Number(e.key));
});

function appuyer(bouton) {
  const touche = touches[bouton - 1];
  touche.classList.add('enfoncee');
  setTimeout(() => touche.classList.remove('enfoncee'), 120);
  if (envoyer({ type: 'appui', bouton })) noter(`Appui sur K${bouton}`);
}

// --- LEDs ---

function afficher(i, [r, g, b]) {
  const allumee = r + g + b > 0;
  touches[i].style.setProperty('--led', allumee ? `rgb(${r} ${g} ${b})` : null);
  touches[i].classList.toggle('allumee', allumee);
}

function clignoter(bouton, couleur, duree) {
  const i = bouton - 1;
  clearTimeout(minuteries[i]);
  afficher(i, couleur);
  minuteries[i] = setTimeout(() => afficher(i, couleurs[i]), duree);
}

function recevoir(message) {
  if (message.type === 'leds') {
    couleurs = message.couleurs;
    couleurs.forEach((couleur, i) => {
      clearTimeout(minuteries[i]);
      afficher(i, couleur);
    });
  } else if (message.type === 'clignoter') {
    clignoter(message.bouton, message.couleur, message.duree);
  } else if (message.type === 'erreur') {
    noter(`Refusé : ${message.message}`);
  }
}

// --- Liaison avec le back ---

function connecter() {
  const protocole = location.protocol === 'https:' ? 'wss' : 'ws';
  lien = new WebSocket(`${protocole}://${location.host}/ws/boitier`);
  lien.onopen = () => marquerConnexion(true);
  lien.onclose = () => {
    marquerConnexion(false);
    setTimeout(connecter, DELAI_RECONNEXION);
  };
  lien.onmessage = (m) => recevoir(JSON.parse(m.data));
}

function envoyer(message) {
  if (lien?.readyState !== WebSocket.OPEN) {
    noter('Pas connecté au back : rien n’a été envoyé.');
    return false;
  }
  lien.send(JSON.stringify(message));
  return true;
}

function marquerConnexion(ouvert) {
  if (ouvert === connecte && etat.className !== 'etat') return;
  connecte = ouvert;
  etat.textContent = ouvert ? 'Connecté au back' : 'Déconnecté, nouvelle tentative…';
  etat.className = `etat ${ouvert ? 'connecte' : 'deconnecte'}`;
  boitier.classList.toggle('hors-ligne', !ouvert);
  noter(ouvert ? 'Connecté au back.' : 'Connexion au back perdue.');
}

// --- Raccourcis de test et journal ---

document.querySelectorAll('[data-action]').forEach((bouton) => {
  bouton.addEventListener('click', () => {
    if (envoyer({ type: 'test', action: bouton.dataset.action })) noter(bouton.textContent);
  });
});

function noter(texte) {
  const ligne = document.createElement('li');
  ligne.textContent = `${new Date().toLocaleTimeString('fr-FR')}  ${texte}`;
  journal.prepend(ligne);
  while (journal.children.length > TAILLE_JOURNAL) journal.lastChild.remove();
}

connecter();
