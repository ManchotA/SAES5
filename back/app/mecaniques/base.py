"""Classe commune à toutes les mécaniques d'énigme."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from app.boitier import Commande, Couleur


@dataclass
class Reponse:
    """Ce que la mécanique renvoie après un événement : énigme résolue ou non, et LEDs à changer."""

    resolue: bool = False
    commandes: list[Commande] = field(default_factory=list)


class Mecanique(ABC):
    """Une énigme en cours dans une salle.

    Une instance est créée à chaque lancement d'énigme, avec les paramètres de la salle
    (champ « parametres » de content/salles.json) et la palette de couleurs du contenu.
    """

    def __init__(self, parametres: dict, couleurs: dict[str, Couleur]) -> None:
        self.parametres = parametres
        self.couleurs = couleurs

    @classmethod
    def verifier_parametres(
        cls, parametres: dict, couleurs: dict[str, Couleur]
    ) -> None:
        """Vérifie les paramètres au chargement du contenu.

        Lève ValueError (ou TypeError pour un champ du mauvais type) s'ils sont invalides.
        """

    def demarrer(self) -> list[Commande]:
        """LEDs à allumer au lancement de l'énigme."""
        return []

    @abstractmethod
    def appui_bouton(self, bouton: int) -> Reponse:
        """Traite l'appui sur un bouton du boîtier."""

    def action(self, donnees: dict) -> Reponse:
        """Action faite à l'écran (souris…), pour les énigmes qui en ont. Ignorée par défaut."""
        return Reponse()

    def tic(self, maintenant: datetime) -> Reponse:
        """Appelée plusieurs fois par seconde, pour les énigmes qui dépendent du temps."""
        return Reponse()

    def etat_public(self) -> dict | None:
        """Avancement visible par le front (sans la solution), ou None."""
        return None
