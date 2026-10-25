"""Chargement et vérification du contenu des salles (content/salles.json)."""

import json
from dataclasses import dataclass, field
from pathlib import Path

from app.mecaniques import MECANIQUES

CHEMIN_SALLES = Path(__file__).resolve().parents[2] / "content" / "salles.json"
ETAGE_FINAL = 4


class ContenuInvalide(Exception):
    """Le fichier de contenu est illisible ou mal formé."""


@dataclass
class Document:
    id: str
    titre: str
    texte: str


@dataclass
class Salle:
    id: str
    etage: int
    nom: str
    mecanique: str
    parametres: dict = field(default_factory=dict)
    documents: list[Document] = field(default_factory=list)

    @property
    def est_finale(self) -> bool:
        return self.etage == ETAGE_FINAL


def charger_salles(chemin: Path = CHEMIN_SALLES) -> dict[str, Salle]:
    """Lit le fichier de contenu et renvoie les salles, rangées par id."""
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as erreur:
        raise ContenuInvalide(f"Impossible de lire {chemin} : {erreur}") from erreur
    return lire_salles(donnees)


def lire_salles(donnees: object) -> dict[str, Salle]:
    """Vérifie le contenu déjà décodé et le transforme en salles."""
    if not isinstance(donnees, dict) or not isinstance(donnees.get("salles"), list):
        raise ContenuInvalide('Le contenu doit être de la forme { "salles": [...] }.')

    salles: dict[str, Salle] = {}
    for brute in donnees["salles"]:
        salle = _lire_salle(brute)
        if salle.id in salles:
            raise ContenuInvalide(f"Identifiant de salle en double : {salle.id}")
        salles[salle.id] = salle

    nb_finales = sum(salle.est_finale for salle in salles.values())
    if nb_finales != 1:
        raise ContenuInvalide(
            f"Il faut exactement une salle à l'étage {ETAGE_FINAL}, il y en a {nb_finales}."
        )
    return salles


def _lire_salle(brute: object) -> Salle:
    try:
        salle = Salle(
            id=brute["id"],
            etage=brute["etage"],
            nom=brute["nom"],
            mecanique=brute["mecanique"],
            parametres=brute.get("parametres", {}),
            documents=[
                Document(id=doc["id"], titre=doc["titre"], texte=doc["texte"])
                for doc in brute.get("documents", [])
            ],
        )
    except (KeyError, TypeError, AttributeError) as erreur:
        raise ContenuInvalide(
            f"Salle mal formée, champ manquant ou invalide : {erreur}"
        ) from erreur

    if salle.etage not in range(1, ETAGE_FINAL + 1):
        raise ContenuInvalide(
            f"Salle {salle.id} : l'étage doit être entre 1 et {ETAGE_FINAL}, pas {salle.etage!r}."
        )
    if salle.mecanique not in MECANIQUES:
        raise ContenuInvalide(
            f"Salle {salle.id} : mécanique inconnue « {salle.mecanique} »."
        )
    return salle
