"""Logique d'une partie : progression dans les étages, énigmes et timer.

L'état renvoyé par Partie.etat() suit le contrat de docs/contrats.md.
"""

from collections.abc import Callable
from datetime import datetime, timedelta
from enum import StrEnum

from app.contenu import ETAGE_FINAL, Salle
from app.mecaniques import MECANIQUES, Mecanique

DUREE_PARTIE = timedelta(minutes=45)


class Statut(StrEnum):
    AUCUNE = "aucune"
    EN_COURS = "en_cours"
    GAGNEE = "gagnee"
    PERDUE = "perdue"


class ErreurPartie(Exception):
    """Action refusée. Le message est lisible par un humain."""


class SalleInconnue(ErreurPartie):
    """Aucune salle ne porte cet identifiant (404 côté API)."""


class ActionImpossible(ErreurPartie):
    """L'action n'est pas possible dans l'état actuel de la partie (409 côté API)."""


class Partie:
    """La partie en cours. Il n'y en a qu'une à la fois.

    `horloge` renvoie l'heure actuelle : les tests en passent une fausse pour simuler
    le temps qui passe. Chaque action revérifie d'abord l'heure, pour qu'aucune action
    ne soit acceptée après la fin du timer.
    """

    def __init__(
        self,
        salles: dict[str, Salle],
        horloge: Callable[[], datetime] = datetime.now,
        duree: timedelta = DUREE_PARTIE,
    ) -> None:
        self.salles = salles
        self.horloge = horloge
        self.duree = duree
        self.statut = Statut.AUCUNE
        self.fin_a: datetime | None = None
        self.salles_resolues: list[str] = []
        self.enigme_en_cours: str | None = None
        self._mecanique: Mecanique | None = None

    def nouvelle(self) -> None:
        """Démarre une nouvelle partie, en effaçant celle en cours s'il y en a une."""
        debut = self.horloge().replace(microsecond=0)
        self.statut = Statut.EN_COURS
        self.fin_a = debut + self.duree
        self.salles_resolues = []
        self._arreter_enigme()

    def lancer_enigme(self, salle_id: str) -> None:
        """Le joueur active le panneau d'une salle : son énigme devient l'énigme en cours.

        Une autre énigme en cours est remplacée, et relancer la même la redémarre.
        """
        self.verifier_temps()
        salle = self._salle(salle_id)
        if self.statut != Statut.EN_COURS:
            raise ActionImpossible("Aucune partie en cours.")
        if salle.etage not in self.etages_ouverts():
            raise ActionImpossible(f"L'étage {salle.etage} n'est pas encore ouvert.")
        if salle_id in self.salles_resolues:
            raise ActionImpossible(f"La salle {salle_id} est déjà résolue.")
        self.enigme_en_cours = salle_id
        self._mecanique = MECANIQUES[salle.mecanique](salle.parametres)

    def annuler_enigme(self, salle_id: str) -> None:
        """Le joueur quitte la salle sans résoudre l'énigme. Sans effet si elle n'est pas en cours."""
        self.verifier_temps()
        self._salle(salle_id)
        if self.enigme_en_cours == salle_id:
            self._arreter_enigme()

    def appui_bouton(self, bouton: int) -> str | None:
        """Transmet un appui du boîtier à l'énigme en cours.

        Renvoie l'id de la salle si cet appui la résout, sinon None.
        L'appui est ignoré s'il n'y a pas d'énigme en cours.
        """
        self.verifier_temps()
        if self._mecanique is None or not self._mecanique.appui_bouton(bouton):
            return None
        salle_id = self.enigme_en_cours
        self.salles_resolues.append(salle_id)
        self._arreter_enigme()
        if self.salles[salle_id].est_finale:
            self.statut = Statut.GAGNEE
        return salle_id

    def verifier_temps(self) -> None:
        """Déclare la défaite si l'heure de fin est atteinte.

        Appelée au début de chaque action, et plus tard régulièrement par le timer du back.
        """
        if self.statut == Statut.EN_COURS and self.horloge() >= self.fin_a:
            self.statut = Statut.PERDUE
            self._arreter_enigme()

    def etages_ouverts(self) -> list[int]:
        """Un étage est ouvert quand toutes les salles des étages du dessous sont résolues."""
        if self.statut == Statut.AUCUNE:
            return []
        return [
            etage
            for etage in range(1, ETAGE_FINAL + 1)
            if all(
                salle.id in self.salles_resolues
                for salle in self.salles.values()
                if salle.etage < etage
            )
        ]

    def etat(self) -> dict:
        """État de la partie au format du contrat."""
        self.verifier_temps()
        return {
            "statut": self.statut.value,
            "fin_a": self.fin_a.isoformat() if self.fin_a else None,
            "etages_ouverts": self.etages_ouverts(),
            "salles_resolues": list(self.salles_resolues),
            "enigme_en_cours": self.enigme_en_cours,
        }

    def _salle(self, salle_id: str) -> Salle:
        try:
            return self.salles[salle_id]
        except KeyError:
            raise SalleInconnue(f"Salle inconnue : {salle_id}") from None

    def _arreter_enigme(self) -> None:
        self.enigme_en_cours = None
        self._mecanique = None
