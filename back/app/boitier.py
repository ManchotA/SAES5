"""Le boîtier à boutons, vu par le back : des intentions (« allumer le bouton 3 en rouge »).

Le back ne connaît pas le format d'échange du vrai boîtier. Il garde l'état des LEDs et
l'envoie aux boîtiers connectés ; pour l'instant, le seul boîtier est le simulateur
(dossier simulateur/), relié par le WebSocket /ws/boitier (voir docs/contrats.md).
"""

import asyncio
import logging
from dataclasses import dataclass

from starlette.websockets import WebSocketDisconnect

NB_BOUTONS = 10
DELAI_ENVOI = 1.0  # secondes : un boîtier qui ne répond pas ne bloque jamais le jeu

# Erreurs possibles en écrivant à un client parti ou bloqué
# (OSError couvre aussi le délai dépassé, TimeoutError)
ERREURS_ENVOI = (OSError, RuntimeError, WebSocketDisconnect)

Couleur = tuple[int, int, int]
NOIR: Couleur = (0, 0, 0)
BLANC: Couleur = (255, 255, 255)
ROUGE: Couleur = (255, 0, 0)
VERT: Couleur = (0, 200, 0)

journal = logging.getLogger(__name__)


@dataclass(frozen=True)
class Allumer:
    """Allume la LED d'un bouton dans une couleur, jusqu'à nouvel ordre."""

    bouton: int
    couleur: Couleur


@dataclass(frozen=True)
class Clignoter:
    """Fait briller la LED d'un bouton un court instant, puis revient à sa couleur."""

    bouton: int
    couleur: Couleur
    duree_ms: int


@dataclass(frozen=True)
class EteindreTout:
    """Éteint toutes les LEDs."""


Commande = Allumer | Clignoter | EteindreTout


class Boitier:
    """État des LEDs et liens avec les boîtiers connectés."""

    def __init__(self, nb_boutons: int = NB_BOUTONS) -> None:
        self.couleurs: list[Couleur] = [NOIR] * nb_boutons
        self._liens: set = set()

    @property
    def connecte(self) -> bool:
        return bool(self._liens)

    async def ajouter(self, lien) -> None:
        """Un boîtier se connecte : il reçoit tout de suite l'état complet des LEDs."""
        self._liens.add(lien)
        await self._envoyer(lien, self._message_leds())

    def retirer(self, lien) -> None:
        self._liens.discard(lien)

    async def appliquer(self, commandes: list[Commande]) -> None:
        """Met à jour l'état des LEDs et le transmet aux boîtiers connectés."""
        if not commandes:
            return
        messages = []
        change = False
        for commande in commandes:
            if isinstance(commande, EteindreTout):
                self.couleurs = [NOIR] * len(self.couleurs)
                change = True
            elif isinstance(commande, Allumer):
                self.couleurs[commande.bouton - 1] = commande.couleur
                change = True
            elif isinstance(commande, Clignoter):
                messages.append(
                    {
                        "type": "clignoter",
                        "bouton": commande.bouton,
                        "couleur": list(commande.couleur),
                        "duree": commande.duree_ms,
                    }
                )
        if change:
            messages.insert(0, self._message_leds())
        for lien in list(self._liens):
            for message in messages:
                await self._envoyer(lien, message)

    def _message_leds(self) -> dict:
        return {"type": "leds", "couleurs": [list(c) for c in self.couleurs]}

    async def _envoyer(self, lien, message: dict) -> None:
        try:
            await asyncio.wait_for(lien.send_json(message), DELAI_ENVOI)
        except ERREURS_ENVOI:
            journal.warning("Boîtier injoignable, lien retiré.")
            self._liens.discard(lien)
