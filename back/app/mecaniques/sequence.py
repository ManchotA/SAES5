"""Mécanique « séquence de couleurs » : reproduire une ou plusieurs suites de couleurs.

Paramètres (champ « parametres » de la salle) :
- boutons : bouton -> nom de couleur de la palette, ex. {"1": "rouge", "2": "vert"} ;
- etapes : une ou plusieurs suites de couleurs, ex. [["rouge", "vert"], ["vert", "vert"]] ;
- erreur (facultatif) :
  - recommencer : "etape" (l'étape en cours repart du début) ou "tout" (toute la séquence).

Seule une étape réussie se voit (les boutons clignotent en vert). Un appui, juste ou faux,
ne donne aucun retour : sinon on pourrait trouver la solution en essayant les touches
une par une.
"""

from app.boitier import NB_BOUTONS, VERT, Allumer, Clignoter, Couleur
from app.mecaniques.base import Mecanique, Reponse

RECOMMENCER = ("etape", "tout")
RECOMMENCER_DEFAUT = "etape"
DUREE_ETAPE_REUSSIE = 400


class MecaniqueSequence(Mecanique):
    def __init__(self, parametres: dict, couleurs: dict[str, Couleur]) -> None:
        super().__init__(parametres, couleurs)
        self.boutons = {int(b): c for b, c in parametres["boutons"].items()}
        self.etapes: list[list[str]] = parametres["etapes"]
        erreur = parametres.get("erreur", {})
        self.recommencer = erreur.get("recommencer", RECOMMENCER_DEFAUT)
        self.etape = 0
        self.position = 0
        self.erreurs = 0  # gardé pour de futures statistiques, jamais montré au joueur

    @classmethod
    def verifier_parametres(
        cls, parametres: dict, couleurs: dict[str, Couleur]
    ) -> None:
        boutons = parametres.get("boutons")
        if not isinstance(boutons, dict) or not boutons:
            raise ValueError(
                "« boutons » doit associer au moins un bouton à une couleur."
            )
        for bouton, couleur in boutons.items():
            if not bouton.isdigit() or not 1 <= int(bouton) <= NB_BOUTONS:
                raise ValueError(f"bouton « {bouton} » invalide, de 1 à {NB_BOUTONS}.")
            if not isinstance(couleur, str) or couleur not in couleurs:
                raise ValueError(f"couleur « {couleur} » absente de la palette.")

        etapes = parametres.get("etapes")
        if (
            not isinstance(etapes, list)
            or not etapes
            or not all(isinstance(etape, list) and etape for etape in etapes)
        ):
            raise ValueError(
                "« etapes » doit être une liste de suites de couleurs non vides."
            )
        sur_un_bouton = set(boutons.values())
        for etape in etapes:
            for couleur in etape:
                if not isinstance(couleur, str) or couleur not in sur_un_bouton:
                    raise ValueError(
                        f"la couleur « {couleur} » d'une étape n'est sur aucun bouton."
                    )

        erreur = parametres.get("erreur", {})
        if not isinstance(erreur, dict):
            raise TypeError("« erreur » doit être un objet.")
        inconnus = set(erreur) - {"recommencer"}
        if inconnus:
            raise ValueError(
                f"réglage d'erreur inconnu : {', '.join(sorted(inconnus))}."
            )
        if erreur.get("recommencer", RECOMMENCER_DEFAUT) not in RECOMMENCER:
            raise ValueError(
                f"« erreur.recommencer » doit valoir {' ou '.join(RECOMMENCER)}."
            )

    def demarrer(self) -> list:
        return [Allumer(b, self.couleurs[c]) for b, c in self.boutons.items()]

    def appui_bouton(self, bouton: int) -> Reponse:
        couleur = self.boutons.get(bouton)
        if couleur is None:  # bouton éteint : sans effet
            return Reponse()

        if couleur != self.etapes[self.etape][self.position]:
            self.erreurs += 1
            if self.recommencer == "tout":
                self.etape = 0
            self.position = 0
            return Reponse()

        self.position += 1
        if self.position < len(self.etapes[self.etape]):
            return Reponse()

        self.etape += 1
        self.position = 0
        if self.etape == len(self.etapes):
            return Reponse(
                resolue=True, commandes=[Allumer(b, VERT) for b in self.boutons]
            )
        return Reponse(
            commandes=[Clignoter(b, VERT, DUREE_ETAPE_REUSSIE) for b in self.boutons]
        )

    def etat_public(self) -> dict:
        """Seulement les étapes réussies : rien qui permette de deviner un appui juste."""
        termine = self.etape == len(self.etapes)
        return {
            "etapes_reussies": self.etape,
            "nb_etapes": len(self.etapes),
            "longueur_etape": 0 if termine else len(self.etapes[self.etape]),
        }
