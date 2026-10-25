"""Mécaniques d'énigme disponibles, rangées par nom (champ « mecanique » de content/salles.json).

Pour ajouter une mécanique : créer une sous-classe de Mecanique dans ce dossier,
puis l'enregistrer dans MECANIQUES.
"""

from app.mecaniques.base import Mecanique
from app.mecaniques.factice import MecaniqueFactice

MECANIQUES: dict[str, type[Mecanique]] = {
    "factice": MecaniqueFactice,
}
