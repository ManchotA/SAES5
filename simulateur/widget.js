// Boîtier virtuel intégré au jeu : une icône en haut à droite qui déplie le simulateur
// par-dessus le jeu, comme un inventaire. Il sert en développement, et de secours à
// l'exposition si le vrai boîtier tombe en panne.
//
// Ctrl + Maj + S affiche ou cache l'icône, sans toucher au code ni relancer quoi que ce
// soit. Le choix est gardé jusqu'à la fermeture du navigateur, même si la page est
// rechargée. Quand l'icône est cachée, le boîtier virtuel est éteint : il n'est pas
// connecté au back et les chiffres du clavier ne font rien.
//
// Par défaut, l'icône est visible en développement (dev.bat) et cachée sinon
// (voir /simulateur/reglages.json, renvoyé par le back).

import { creerSimulateur } from './simulateur.js';

const CLE_VISIBLE = 'boitier-virtuel.visible';
const URL_STYLE = new URL('./simulateur.css', import.meta.url);
const ETEINTE = [0, 0, 0];

const reglages = await fetch(new URL('./reglages.json', import.meta.url))
  .then((reponse) => reponse.json())
  .catch(() => ({}));

const hote = document.createElement('div');
hote.id = 'boitier-virtuel';
document.body.append(hote);

const racine = hote.attachShadow({ mode: 'open' });
racine.innerHTML = `
  <link rel="stylesheet" href="${URL_STYLE}" />
  <div class="widget">
    <button type="button" class="icone" aria-expanded="false"
            title="Boîtier virtuel (Ctrl + Maj + S pour cacher l'icône)">
      <svg viewBox="0 0 29 12" aria-hidden="true">
        ${Array.from({ length: 10 }, (_, i) => {
          const x = (i % 5) * 6;
          const y = Math.floor(i / 5) * 7;
          return `<rect x="${x}" y="${y}" width="5" height="5" rx="1.2" />`;
        }).join('')}
      </svg>
      <span class="voyant"></span>
    </button>
    <div class="panneau"></div>
  </div>`;

const widget = racine.querySelector('.widget');
const icone = racine.querySelector('.icone');
const carres = racine.querySelectorAll('rect');

const simulateur = creerSimulateur(racine.querySelector('.panneau'), {
  outilsDeTest: Boolean(reglages.outils_de_test),
  surConnexion: (ouvert) => icone.classList.toggle('connecte', ouvert),
  surLeds: (couleurs) => couleurs.forEach((couleur, i) => colorerCarre(i, couleur)),
});

let visible = lireMemoire() ?? Boolean(reglages.visible_par_defaut);
appliquerVisibilite();

icone.addEventListener('click', () => ouvrir(!widget.classList.contains('ouvert')));

document.addEventListener('pointerdown', (e) => {
  if (!e.composedPath().includes(hote)) ouvrir(false);
});

document.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.shiftKey && e.code === 'KeyS') {
    e.preventDefault();
    visible = !visible;
    ecrireMemoire(visible);
    appliquerVisibilite();
  } else if (e.key === 'Escape') {
    ouvrir(false);
  }
});

function appliquerVisibilite() {
  widget.hidden = !visible;
  if (visible) {
    simulateur.activer();
  } else {
    ouvrir(false);
    simulateur.desactiver();
    carres.forEach((_, i) => colorerCarre(i, ETEINTE));
  }
}

function ouvrir(ouvert) {
  widget.classList.toggle('ouvert', ouvert);
  icone.setAttribute('aria-expanded', String(ouvert));
}

function colorerCarre(i, [r, g, b]) {
  carres[i].style.fill = r + g + b > 0 ? `rgb(${r} ${g} ${b})` : '';
}

function lireMemoire() {
  try {
    const valeur = sessionStorage.getItem(CLE_VISIBLE);
    return valeur === null ? null : valeur === '1';
  } catch {
    return null;
  }
}

function ecrireMemoire(valeur) {
  try {
    sessionStorage.setItem(CLE_VISIBLE, valeur ? '1' : '0');
  } catch {
    // stockage indisponible : le choix vaut seulement pour cette page
  }
}
