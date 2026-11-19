"""Mécanique provisoire, en attendant les vraies : un appui sur le bouton 1 résout l'énigme."""

from app.mecaniques.base import Mecanique, Reponse

BOUTON_SOLUTION = 1


class MecaniqueFactice(Mecanique):
    def appui_bouton(self, bouton: int) -> Reponse:
        return Reponse(resolue=bouton == BOUTON_SOLUTION)
