from datetime import datetime, timedelta

import pytest

from app.contenu import Salle
from app.partie import Partie

DEBUT = datetime(2026, 10, 25, 15, 0, 0)


class FausseHorloge:
    """Horloge des tests : le temps n'avance que quand on le demande."""

    def __init__(self, depart: datetime = DEBUT) -> None:
        self.maintenant = depart

    def __call__(self) -> datetime:
        return self.maintenant

    def avancer(self, **duree: float) -> None:
        self.maintenant += timedelta(**duree)


@pytest.fixture
def horloge() -> FausseHorloge:
    return FausseHorloge()


@pytest.fixture
def salles() -> dict[str, Salle]:
    """Petit bâtiment de test, indépendant de content/salles.json.

    2 salles à l'étage 1, puis 1 salle par étage jusqu'à la finale.
    """
    liste = [
        Salle(id="e1_a", etage=1, nom="A", mecanique="factice"),
        Salle(id="e1_b", etage=1, nom="B", mecanique="factice"),
        Salle(id="e2_a", etage=2, nom="C", mecanique="factice"),
        Salle(id="e3_a", etage=3, nom="D", mecanique="factice"),
        Salle(id="finale", etage=4, nom="Finale", mecanique="factice"),
    ]
    return {salle.id: salle for salle in liste}


@pytest.fixture
def partie(salles, horloge) -> Partie:
    """Une partie qui vient de commencer."""
    partie = Partie(salles, horloge)
    partie.nouvelle()
    return partie
