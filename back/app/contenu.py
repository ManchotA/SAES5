"""Chargement et vérification du contenu du jeu (content/salles.json).

Le fichier contient une palette de couleurs nommées et la liste des salles.
Toute erreur est signalée au démarrage, avec la salle en cause.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

from app.boitier import Couleur
from app.mecaniques import MECANIQUES

CHEMIN_CONTENU = Path(__file__).resolve().parents[2] / "content" / "salles.json"
ETAGE_TUTO = 0
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

    def partie_publique(self) -> dict:
        """Ce que le front a le droit de voir : jamais la mécanique ni ses paramètres."""
        return {
            "id": self.id,
            "etage": self.etage,
            "nom": self.nom,
            "documents": [vars(doc) for doc in self.documents],
        }


@dataclass
class Contenu:
    couleurs: dict[str, Couleur]
    salles: dict[str, Salle]


def charger_contenu(chemin: Path = CHEMIN_CONTENU) -> Contenu:
    """Lit et vérifie le fichier de contenu."""
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as erreur:
        raise ContenuInvalide(f"Impossible de lire {chemin} : {erreur}") from erreur
    return lire_contenu(donnees)


def lire_contenu(donnees: object) -> Contenu:
    """Vérifie le contenu déjà décodé et le transforme en palette et en salles."""
    if not isinstance(donnees, dict) or not isinstance(donnees.get("salles"), list):
        raise ContenuInvalide('Le contenu doit être de la forme { "salles": [...] }.')

    couleurs = _lire_couleurs(donnees.get("couleurs", {}))
    salles: dict[str, Salle] = {}
    for brute in donnees["salles"]:
        salle = _lire_salle(brute, couleurs)
        if salle.id in salles:
            raise ContenuInvalide(f"Identifiant de salle en double : {salle.id}")
        salles[salle.id] = salle

    nb_finales = sum(salle.est_finale for salle in salles.values())
    if nb_finales != 1:
        raise ContenuInvalide(
            f"Il faut exactement une salle à l'étage {ETAGE_FINAL}, il y en a {nb_finales}."
        )
    return Contenu(couleurs=couleurs, salles=salles)


def _lire_couleurs(brutes: object) -> dict[str, Couleur]:
    if not isinstance(brutes, dict):
        raise ContenuInvalide(
            "« couleurs » doit associer un nom à [rouge, vert, bleu]."
        )
    couleurs = {}
    for nom, rvb in brutes.items():
        if (
            not isinstance(rvb, list)
            or len(rvb) != 3
            or not all(isinstance(v, int) and 0 <= v <= 255 for v in rvb)
        ):
            raise ContenuInvalide(
                f"Couleur « {nom} » : il faut trois nombres entre 0 et 255, pas {rvb!r}."
            )
        couleurs[nom] = tuple(rvb)
    return couleurs


def _lire_salle(brute: object, couleurs: dict[str, Couleur]) -> Salle:
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

    if salle.etage not in range(ETAGE_TUTO, ETAGE_FINAL + 1):
        raise ContenuInvalide(
            f"Salle {salle.id} : l'étage doit être entre {ETAGE_TUTO} et {ETAGE_FINAL}, "
            f"pas {salle.etage!r}."
        )
    mecanique = MECANIQUES.get(salle.mecanique)
    if mecanique is None:
        raise ContenuInvalide(
            f"Salle {salle.id} : mécanique inconnue « {salle.mecanique} »."
        )
    if not isinstance(salle.parametres, dict):
        raise ContenuInvalide(f"Salle {salle.id} : « parametres » doit être un objet.")
    try:
        mecanique.verifier_parametres(salle.parametres, couleurs)
    except (TypeError, ValueError) as erreur:
        raise ContenuInvalide(f"Salle {salle.id} : {erreur}") from erreur
    return salle
