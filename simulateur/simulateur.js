// Simulateur du boîtier : 10 touches avec LED, reliées au back par le WebSocket /ws/boitier.
// Le format des messages est décrit dans docs/contrats.md (§5).
//
// Ce module dessine le boîtier dans un élément de la page, isolé dans un shadow DOM pour
// que ses styles ne se mélangent jamais avec ceux de la page qui l'accueille. Il sert à la
// fois à la page simulateur/index.html et à l'icône intégrée au jeu (widget.js).

const NB_BOUTONS = 10;
const ETEINTE = [0, 0, 0];
const DELAI_RECONNEXION = 2000;
const TAILLE_JOURNAL = 30;
const URL_STYLE = new URL('./simulateur.css', import.meta.url);

/**
 * Dessine le boîtier dans `hote`. Il ne fait rien tant qu'on ne l'a pas activé :
 * activer() le connecte au back et écoute les chiffres du clavier, desactiver() l'éteint.
 *
 * Options : outilsDeTest (affiche « résoudre » et « perdre »), surConnexion(ouvert),
 * surLeds(couleurs).
 */
export function creerSimulateur(
  hote,
  { outilsDeTest = false, surConnexion = () => {}, surLeds = () => {} } = {},
) {
  const racine = hote.attachShadow({ mode: 'open' });
  racine.innerHTML = `
    <link rel="stylesheet" href="${URL_STYLE}" />
    <section class="boitier hors-ligne" aria-label="Boîtier">
      <header class="entete">
        <h2>Boîtier</h2>
        <p class="etat">Éteint</p>
      </header>
      <div class="touches"></div>
      <p class="aide">Clique sur une touche, ou tape les chiffres 1 à 0.</p>
      <div class="outils" ${outilsDeTest ? '' : 'hidden'}>
        <button type="button" data-action="resoudre">Résoudre l'énigme en cours</button>
        <button type="button" data-action="perdre">Faire perdre la partie</button>
      </div>
      <details>
        <summary>Journal</summary>
        <ol class="journal"></ol>
      </details>
    </section>`;

  const boitier = racine.querySelector('.boitier');
  const etat = racine.querySelector('.etat');
  const journal = racine.querySelector('.journal');
  const touches = [];
  const minuteries = [];
  let couleurs = Array.from({ length: NB_BOUTONS }, () => ETEINTE);
  let lien = null;
  let actif = false;
  let connecte = null;
  let reconnexion = null;

  // --- Touches ---

  for (let bouton = 1; bouton <= NB_BOUTONS; bouton++) {
    const touche = document.createElement('button');
    touche.type = 'button';
    touche.className = 'touche';
    touche.innerHTML = `<span class="numero">K${bouton}</span><span class="clavier">${bouton % 10}</span>`;
    touche.addEventListener('pointerdown', (e) => {
      e.preventDefault(); // garde le focus sur le jeu
      appuyer(bouton);
    });
    racine.querySelector('.touches').append(touche);
    touches.push(touche);
  }

  function surClavier(e) {
    if (e.repeat || e.ctrlKey || e.altKey || e.metaKey || !/^[0-9]$/.test(e.key)) return;
    appuyer(e.key === '0' ? 10 : Number(e.key));
  }

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
      surLeds(couleurs);
    } else if (message.type === 'clignoter') {
      clignoter(message.bouton, message.couleur, message.duree);
    } else if (message.type === 'erreur') {
      noter(`Refusé : ${message.message}`);
    }
  }

  // --- Liaison avec le back ---

  function activer() {
    if (actif) return;
    actif = true;
    document.addEventListener('keydown', surClavier);
    connecter();
  }

  function desactiver() {
    if (!actif) return;
    actif = false;
    clearTimeout(reconnexion);
    document.removeEventListener('keydown', surClavier);
    lien?.close();
    marquerConnexion(false, 'Éteint');
  }

  function connecter() {
    if (!actif) return;
    const protocole = location.protocol === 'https:' ? 'wss' : 'ws';
    const nouveau = new WebSocket(`${protocole}://${location.host}/ws/boitier`);
    lien = nouveau;
    nouveau.onopen = () => marquerConnexion(true);
    nouveau.onclose = () => {
      if (lien !== nouveau || !actif) return;
      marquerConnexion(false);
      reconnexion = setTimeout(connecter, DELAI_RECONNEXION);
    };
    nouveau.onmessage = (m) => recevoir(JSON.parse(m.data));
  }

  function envoyer(message) {
    if (lien?.readyState !== WebSocket.OPEN) {
      noter('Pas connecté au back : rien n’a été envoyé.');
      return false;
    }
    lien.send(JSON.stringify(message));
    return true;
  }

  function marquerConnexion(ouvert, texte) {
    const changement = ouvert !== connecte;
    connecte = ouvert;
    etat.textContent = texte ?? (ouvert ? 'Connecté au back' : 'Déconnecté, nouvelle tentative…');
    etat.className = `etat ${ouvert ? 'connecte' : 'deconnecte'}`;
    boitier.classList.toggle('hors-ligne', !ouvert);
    if (changement) {
      noter(ouvert ? 'Connecté au back.' : 'Déconnecté du back.');
      surConnexion(ouvert);
    }
  }

  // --- Raccourcis de test et journal ---

  racine.querySelectorAll('[data-action]').forEach((bouton) => {
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

  return { activer, desactiver };
}
