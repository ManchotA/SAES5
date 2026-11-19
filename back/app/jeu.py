"""Relie la partie, le boîtier et les écrans connectés.

Toute action qui touche la partie passe par Jeu.executer : elle prend le verrou, puis
envoie au boîtier les LEDs à changer et aux écrans les événements survenus, avec l'état
complet de la partie (docs/contrats.md, §3 et §6). Chaque envoi a un délai maximum,
pour que le verrou soit toujours libéré.
"""

import asyncio
import logging
from collections.abc import Callable

from app.boitier import DELAI_ENVOI, ERREURS_ENVOI, Boitier
from app.partie import Partie

journal = logging.getLogger(__name__)


class Jeu:
    def __init__(self, partie: Partie, boitier: Boitier) -> None:
        self.partie = partie
        self.boitier = boitier
        self.verrou = asyncio.Lock()
        self.ecrans: set = set()
        self.outils_de_test: dict[str, Callable[[], None]] = {
            "resoudre": partie.resoudre_enigme_en_cours,
            "perdre": partie.declarer_defaite,
        }

    async def executer(self, action: Callable[[], object]) -> dict:
        """Exécute une action sur la partie sous le verrou, publie ses effets et renvoie l'état."""
        async with self.verrou:
            try:
                action()
            finally:
                etat = await self._publier()
        return etat

    async def message_boitier(self, message: object) -> None:
        """Traite un message du boîtier (docs/contrats.md, §5). Les messages inconnus sont ignorés."""
        if not isinstance(message, dict):
            return
        if message.get("type") == "appui" and isinstance(message.get("bouton"), int):
            bouton = message["bouton"]
            await self.executer(lambda: self.partie.appui_bouton(bouton))
        elif (
            message.get("type") == "test"
            and message.get("action") in self.outils_de_test
        ):
            await self.executer(self.outils_de_test[message["action"]])

    async def connecter_boitier(self, lien) -> None:
        async with self.verrou:
            premier = not self.boitier.connecte
            await self.boitier.ajouter(lien)
            await self._publier([{"type": "boitier_reconnecte"}] if premier else [])

    async def deconnecter_boitier(self, lien) -> None:
        async with self.verrou:
            self.boitier.retirer(lien)
            dernier = not self.boitier.connecte
            await self._publier([{"type": "boitier_deconnecte"}] if dernier else [])

    async def surveiller_temps(self, intervalle: float) -> None:
        """Tâche de fond : fin du timer et énigmes qui dépendent du temps."""
        while True:
            try:
                await self.executer(self.partie.tic)
            # Volontairement large : quoi qu'il arrive, la tâche du timer ne doit pas s'arrêter
            except Exception:  # noqa: BLE001
                journal.exception("Erreur dans la tâche du timer.")
            await asyncio.sleep(intervalle)

    async def _publier(self, autres_evenements: list[dict] | None = None) -> dict:
        etat = self.partie.etat()
        await self.boitier.appliquer(self.partie.prendre_commandes())
        for evenement in [
            *self.partie.prendre_evenements(),
            *(autres_evenements or []),
        ]:
            await self._diffuser({**evenement, "partie": etat})
        return etat

    async def _diffuser(self, message: dict) -> None:
        for ecran in list(self.ecrans):
            try:
                await asyncio.wait_for(ecran.send_json(message), DELAI_ENVOI)
            except ERREURS_ENVOI:
                journal.warning("Écran injoignable, connexion retirée.")
                self.ecrans.discard(ecran)
