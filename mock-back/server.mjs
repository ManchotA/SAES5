import http from 'node:http';
import { WebSocketServer } from 'ws';

const PORT = 8000;
const DUREE_MS = 15 * 60_000;   // durée de la partie : 15 minutes

// Partie publique du contenu : jamais mecanique ni parametres (contrat §2)
const SALLES = [
  ...[1, 2, 3].flatMap(e => [1, 2, 3].map(n => ({
    id: `e${e}_salle${n}`, etage: e, nom: `Salle ${e}.${n}`,
    documents: e === 1 && n === 1
      ? [{ id: 'note', titre: 'Note provisoire', texte: 'Document de test.' }] : [],
  }))),
  { id: 'e4_finale', etage: 4, nom: 'Salle finale', documents: [] },
];

const partieVide = () => ({
  statut: 'aucune', fin_a: null, etages_ouverts: [], salles_resolues: [], enigme_en_cours: null,
});
let partie = partieVide();
let timer;

// ---------- WebSocket : chaque message porte l'état complet (contrat §3) ----------
const wss = new WebSocketServer({ noServer: true });
function diffuser(type, salle) {
  const msg = JSON.stringify({ type, ...(salle ? { salle } : {}), partie });
  wss.clients.forEach(c => c.readyState === 1 && c.send(msg));
  console.log('WS →', type, salle ?? '');
}

// ---------- Logique de partie ----------
function demarrer() {
  clearTimeout(timer);
  partie = {
    statut: 'en_cours',
    fin_a: new Date(Date.now() + DUREE_MS).toISOString(),
    etages_ouverts: [1], salles_resolues: [], enigme_en_cours: null,
  };
  timer = setTimeout(() => {
    if (partie.statut === 'en_cours') { partie.statut = 'perdue'; diffuser('partie_terminee'); }
  }, DUREE_MS);
}

function resoudre(id) {
  partie.salles_resolues = [...new Set([...partie.salles_resolues, id])];
  partie.enigme_en_cours = null;
  const resolu = e => SALLES.filter(s => s.etage === e).every(s => partie.salles_resolues.includes(s.id));
  partie.etages_ouverts = [1, 2, 3, 4].filter(e => e === 1 || resolu(e - 1));
  diffuser('enigme_resolue', id);
  if (id === 'e4_finale') { partie.statut = 'gagnee'; diffuser('partie_terminee'); }
}

// ---------- Page du simulateur de boîtier ----------
const PAGE = `<!doctype html><meta charset="utf-8"><title>Simulateur boîtier</title>
<body style="font-family:sans-serif;max-width:480px;margin:2rem auto">
<h2>Simulateur de boîtier</h2>
<p><button onclick="a('resoudre')">Résoudre l'énigme en cours</button></p>
<p><button onclick="a('deconnecter')">Déconnecter le boîtier</button>
   <button onclick="a('reconnecter')">Reconnecter</button></p>
<p><button onclick="a('perdre')">Temps écoulé (défaite)</button></p>
<pre id="o"></pre>
<script>async function a(x){const r=await fetch('/simu/'+x,{method:'POST'});
document.getElementById('o').textContent=r.status+' '+await r.text();}</script></body>`;

// ---------- Routes REST (contrat §2) ----------
const json = (res, code, body) => {
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(body));
};

const server = http.createServer((req, res) => {
  const { pathname } = new URL(req.url, 'http://localhost');
  const m = req.method;
  console.log(m, pathname);

  if (m === 'GET' && pathname === '/api/sante') return json(res, 200, { statut: 'ok' });
  if (m === 'GET' && pathname === '/api/salles') return json(res, 200, SALLES);

  if (pathname === '/api/partie') {
    if (m === 'GET') return json(res, 200, partie);
    if (m === 'POST') { demarrer(); return json(res, 200, partie); }
  }

  const r = pathname.match(/^\/api\/partie\/salles\/([^/]+)\/enigme$/);
  if (r) {
    const id = r[1];
    const salle = SALLES.find(s => s.id === id);
    if (!salle) return json(res, 404, { erreur: 'Salle inconnue' });

    if (m === 'POST') {
      if (partie.statut !== 'en_cours') return json(res, 409, { erreur: 'Aucune partie en cours' });
      if (!partie.etages_ouverts.includes(salle.etage)) return json(res, 409, { erreur: 'Étage fermé' });
      if (partie.salles_resolues.includes(id)) return json(res, 409, { erreur: 'Salle déjà résolue' });
      if (partie.enigme_en_cours && partie.enigme_en_cours !== id)
        return json(res, 409, { erreur: 'Une autre énigme est en cours' });
      partie.enigme_en_cours = id;
      return json(res, 200, partie);
    }
    if (m === 'DELETE') {
      if (partie.enigme_en_cours === id) partie.enigme_en_cours = null;
      return json(res, 200, partie);
    }
  }

  // ---------- Simulateur ----------
  if (m === 'GET' && pathname === '/simulateur') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(PAGE);
  }
  if (m === 'POST' && pathname.startsWith('/simu/')) {
    const action = pathname.slice(6);
    if (action === 'resoudre') {
      if (!partie.enigme_en_cours) return json(res, 409, { erreur: 'Aucune énigme en cours' });
      resoudre(partie.enigme_en_cours);
    } else if (action === 'perdre') {
      if (partie.statut !== 'en_cours') return json(res, 409, { erreur: 'Aucune partie en cours' });
      partie.statut = 'perdue'; diffuser('partie_terminee');
    } else if (action === 'deconnecter') diffuser('boitier_deconnecte');
    else if (action === 'reconnecter') diffuser('boitier_reconnecte');
    else return json(res, 404, { erreur: 'Action inconnue' });
    return json(res, 200, partie);
  }

  json(res, 404, { erreur: 'Route inconnue' });
});

server.on('upgrade', (req, socket, head) => {
  if (req.url === '/ws') wss.handleUpgrade(req, socket, head, ws => wss.emit('connection', ws));
  else socket.destroy();
});

server.listen(PORT, () => {
  console.log(`Faux back sur http://localhost:${PORT}`);
  console.log(`Simulateur de boîtier : http://localhost:${PORT}/simulateur`);
});