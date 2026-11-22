"""Serveur du jeu : routes REST, WebSockets et tâche du timer (voir docs/contrats.md).

Lancement en développement, depuis back/ (ou avec dev.bat à la racine) :
    .venv\\Scripts\\python -m uvicorn app.main:app --reload --port 8000

Variables d'environnement :
- ESCAPE_DUREE_MINUTES : durée d'une partie (45 par défaut) ;
- ESCAPE_DEV=1 (mis par dev.bat) : mode développement, où l'icône du boîtier virtuel est
  visible par défaut et où les raccourcis de test du simulateur sont acceptés.
"""

import asyncio
import json
import os
from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.boitier import Boitier
from app.contenu import charger_contenu
from app.jeu import Jeu
from app.partie import DUREE_PARTIE, ErreurPartie, Partie, SalleInconnue

DOSSIER_SIMULATEUR = Path(__file__).resolve().parents[2] / "simulateur"
INTERVALLE_TIMER = 0.2  # secondes entre deux vérifications du temps


def duree_configuree() -> timedelta:
    minutes = os.environ.get("ESCAPE_DUREE_MINUTES")
    return timedelta(minutes=float(minutes)) if minutes else DUREE_PARTIE


def creer_app(
    partie: Partie | None = None,
    intervalle_timer: float = INTERVALLE_TIMER,
    mode_dev: bool | None = None,
) -> FastAPI:
    """Construit le serveur. Les tests passent leur propre partie (fausse horloge…)."""
    if partie is None:
        partie = Partie(charger_contenu(), duree=duree_configuree())
    if mode_dev is None:
        mode_dev = os.environ.get("ESCAPE_DEV") == "1"
    jeu = Jeu(partie, Boitier(), outils_de_test=mode_dev)

    @asynccontextmanager
    async def cycle_de_vie(app: FastAPI):
        tache = asyncio.create_task(jeu.surveiller_temps(intervalle_timer))
        yield
        tache.cancel()

    app = FastAPI(title="Escape game", lifespan=cycle_de_vie)
    app.state.jeu = jeu

    @app.exception_handler(ErreurPartie)
    async def erreur_partie(request: Request, erreur: ErreurPartie) -> JSONResponse:
        code = 404 if isinstance(erreur, SalleInconnue) else 409
        return JSONResponse(status_code=code, content={"erreur": str(erreur)})

    # --- Routes REST (contrat §2) ---

    @app.get("/api/sante")
    async def sante() -> dict:
        return {"statut": "ok"}

    @app.get("/api/salles")
    async def salles() -> list[dict]:
        return [salle.partie_publique() for salle in partie.salles.values()]

    @app.get("/api/partie")
    async def lire_partie() -> dict:
        return await jeu.executer(lambda: None)

    @app.post("/api/partie")
    async def nouvelle_partie() -> dict:
        return await jeu.executer(partie.nouvelle)

    @app.post("/api/partie/salles/{salle_id}/enigme")
    async def lancer_enigme(salle_id: str) -> dict:
        return await jeu.executer(lambda: partie.lancer_enigme(salle_id))

    @app.delete("/api/partie/salles/{salle_id}/enigme")
    async def annuler_enigme(salle_id: str) -> dict:
        return await jeu.executer(lambda: partie.annuler_enigme(salle_id))

    # --- WebSockets (contrat §3 et §5) ---

    @app.websocket("/ws")
    async def ws_ecran(lien: WebSocket) -> None:
        await lien.accept()
        jeu.ecrans.add(lien)
        try:
            # Le front n'envoie rien : on attend seulement sa déconnexion
            while True:
                await lien.receive_text()
        except WebSocketDisconnect:
            jeu.ecrans.discard(lien)

    @app.websocket("/ws/boitier")
    async def ws_boitier(lien: WebSocket) -> None:
        await lien.accept()
        await jeu.connecter_boitier(lien)
        try:
            while True:
                texte = await lien.receive_text()
                try:
                    message = json.loads(texte)
                except ValueError:
                    continue
                try:
                    await jeu.message_boitier(message)
                except ErreurPartie as erreur:
                    await lien.send_json({"type": "erreur", "message": str(erreur)})
        except WebSocketDisconnect:
            await jeu.deconnecter_boitier(lien)

    # --- Simulateur du boîtier (page seule et icône dans le jeu) ---

    @app.get("/simulateur/reglages.json")
    async def reglages_simulateur() -> dict:
        return {"visible_par_defaut": mode_dev, "outils_de_test": mode_dev}

    if DOSSIER_SIMULATEUR.is_dir():
        app.mount(
            "/simulateur",
            StaticFiles(directory=DOSSIER_SIMULATEUR, html=True),
            name="simulateur",
        )

    return app


app = creer_app()
