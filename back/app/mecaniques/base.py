"""Classe commune à toutes les mécaniques d'énigme."""

from abc import ABC, abstractmethod


class Mecanique(ABC):
    """Une énigme en cours dans une salle.

    Une instance est créée à chaque lancement d'énigme, avec les paramètres de la salle
    (champ « parametres » de content/salles.json).
    """

    def __init__(self, parametres: dict) -> None:
        self.parametres = parametres

    @abstractmethod
    def appui_bouton(self, bouton: int) -> bool:
        """Traite l'appui sur un bouton du boîtier. Renvoie True si l'énigme est résolue."""
