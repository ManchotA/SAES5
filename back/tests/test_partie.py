import json
from datetime import datetime

import pytest

from app.boitier import Allumer, EteindreTout
from app.contenu import Contenu, Salle
from app.mecaniques import MECANIQUES, Mecanique, Reponse
from app.partie import ActionImpossible, Partie, SalleInconnue

PALETTE = {"rouge": (255, 0, 0), "vert": (0, 200, 0)}


def resoudre(partie: Partie, salle_id: str) -> None:
    """Lance l'énigme d'une salle et la résout (le bouton 1 résout la mécanique factice)."""
    partie.lancer_enigme(salle_id)
    assert partie.appui_bouton(1) == salle_id


def partie_de(horloge, *salles: Salle) -> Partie:
    """Une partie commencée sur ces salles, plus une finale factice, sans rien en attente."""
    liste = [*salles, Salle(id="finale", etage=4, nom="Finale", mecanique="factice")]
    partie = Partie(Contenu(couleurs=PALETTE, salles={s.id: s for s in liste}), horloge)
    partie.nouvelle()
    partie.prendre_commandes()
    partie.prendre_evenements()
    return partie


def salle_sequence() -> Salle:
    """Deux étapes : rouge puis vert, puis vert seul."""
    return Salle(
        id="seq",
        etage=1,
        nom="Séquence",
        mecanique="sequence",
        parametres={
            "boutons": {"1": "rouge", "2": "vert"},
            "etapes": [["rouge", "vert"], ["vert"]],
        },
    )


# --- Nouvelle partie ---


def test_etat_avant_toute_partie(contenu, horloge):
    assert Partie(contenu, horloge).etat() == {
        "statut": "aucune",
        "fin_a": None,
        "etages_ouverts": [],
        "salles_resolues": [],
        "enigme_en_cours": None,
        "enigme_etat": None,
    }


def test_nouvelle_partie(partie):
    assert partie.etat() == {
        "statut": "en_cours",
        "fin_a": "2026-10-25T15:45:00",
        "etages_ouverts": [1],
        "salles_resolues": [],
        "enigme_en_cours": None,
        "enigme_etat": None,
    }


def test_nouvelle_partie_eteint_les_leds(partie):
    assert partie.prendre_commandes() == [EteindreTout()]


def test_heure_de_fin_arrondie_a_la_seconde(contenu, horloge):
    horloge.maintenant = datetime(2026, 10, 25, 15, 0, 0, 999_999)
    partie = Partie(contenu, horloge)
    partie.nouvelle()
    assert partie.etat()["fin_a"] == "2026-10-25T15:45:00"


def test_nouvelle_partie_remet_tout_a_zero(partie, horloge):
    resoudre(partie, "e1_a")
    partie.lancer_enigme("e1_b")
    horloge.avancer(minutes=10)

    partie.nouvelle()

    etat = partie.etat()
    assert etat["fin_a"] == "2026-10-25T15:55:00"
    assert etat["salles_resolues"] == []
    assert etat["enigme_en_cours"] is None


def test_l_etat_est_serialisable_en_json(horloge):
    partie = partie_de(horloge, salle_sequence())
    partie.lancer_enigme("seq")
    assert json.loads(json.dumps(partie.etat())) == partie.etat()


# --- Lancer une énigme ---


def test_lancer_une_enigme(partie):
    partie.lancer_enigme("e1_a")
    assert partie.etat()["enigme_en_cours"] == "e1_a"


def test_lancer_une_enigme_allume_ses_leds(horloge):
    partie = partie_de(horloge, salle_sequence())
    partie.lancer_enigme("seq")
    assert partie.prendre_commandes() == [
        EteindreTout(),
        Allumer(1, (255, 0, 0)),
        Allumer(2, (0, 200, 0)),
    ]


def test_lancer_une_salle_inconnue(partie):
    with pytest.raises(SalleInconnue):
        partie.lancer_enigme("nexiste_pas")


def test_lancer_sans_partie_en_cours(contenu, horloge):
    with pytest.raises(ActionImpossible):
        Partie(contenu, horloge).lancer_enigme("e1_a")


def test_lancer_dans_un_etage_ferme(partie):
    with pytest.raises(ActionImpossible):
        partie.lancer_enigme("e2_a")


def test_lancer_une_salle_deja_resolue(partie):
    resoudre(partie, "e1_a")
    with pytest.raises(ActionImpossible):
        partie.lancer_enigme("e1_a")


def test_lancer_une_enigme_remplace_celle_en_cours(partie):
    partie.lancer_enigme("e1_a")
    partie.lancer_enigme("e1_b")

    assert partie.appui_bouton(1) == "e1_b"
    assert partie.etat()["salles_resolues"] == ["e1_b"]


def test_relancer_la_meme_enigme_la_redemarre(horloge):
    partie = partie_de(horloge, salle_sequence())
    partie.lancer_enigme("seq")
    partie.appui_bouton(1)
    partie.appui_bouton(2)
    assert partie.etat()["enigme_etat"]["etapes_reussies"] == 1

    partie.lancer_enigme("seq")
    assert partie.etat()["enigme_etat"]["etapes_reussies"] == 0


# --- Annuler une énigme ---


def test_annuler_l_enigme_en_cours(partie):
    partie.lancer_enigme("e1_a")
    partie.prendre_commandes()
    partie.annuler_enigme("e1_a")

    assert partie.etat()["enigme_en_cours"] is None
    assert partie.prendre_commandes() == [EteindreTout()]
    assert partie.appui_bouton(1) is None
    assert partie.etat()["salles_resolues"] == []


def test_annuler_une_salle_inconnue(partie):
    with pytest.raises(SalleInconnue):
        partie.annuler_enigme("nexiste_pas")


def test_annuler_une_autre_salle_ne_fait_rien(partie):
    partie.lancer_enigme("e1_a")
    partie.annuler_enigme("e1_b")
    assert partie.etat()["enigme_en_cours"] == "e1_a"


def test_annuler_une_salle_deja_resolue_ne_fait_rien(partie):
    resoudre(partie, "e1_a")
    partie.annuler_enigme("e1_a")
    assert partie.etat()["salles_resolues"] == ["e1_a"]


# --- Résoudre une salle ---


def test_resoudre_une_salle(partie):
    partie.lancer_enigme("e1_a")
    partie.prendre_evenements()

    assert partie.appui_bouton(1) == "e1_a"
    assert partie.etat()["salles_resolues"] == ["e1_a"]
    assert partie.etat()["enigme_en_cours"] is None
    assert partie.prendre_evenements() == [{"type": "enigme_resolue", "salle": "e1_a"}]


def test_un_mauvais_bouton_ne_resout_pas(partie):
    partie.lancer_enigme("e1_a")

    assert partie.appui_bouton(2) is None
    assert partie.etat()["enigme_en_cours"] == "e1_a"
    assert partie.etat()["salles_resolues"] == []


def test_un_appui_sans_enigme_est_ignore(partie):
    assert partie.appui_bouton(1) is None
    assert partie.etat()["salles_resolues"] == []


def test_une_etape_reussie_est_diffusee(horloge):
    partie = partie_de(horloge, salle_sequence())
    partie.lancer_enigme("seq")

    partie.appui_bouton(1)
    partie.appui_bouton(2)

    assert partie.prendre_evenements() == [
        {"type": "enigme_progression", "salle": "seq"}
    ]
    assert partie.etat()["enigme_etat"]["etapes_reussies"] == 1


def test_un_appui_juste_ou_faux_n_est_pas_diffuse(horloge):
    partie = partie_de(horloge, salle_sequence())
    partie.lancer_enigme("seq")

    partie.appui_bouton(1)  # juste
    partie.appui_bouton(1)  # faux

    assert partie.prendre_evenements() == []


def test_un_appui_sans_effet_n_est_pas_diffuse(horloge):
    partie = partie_de(horloge, salle_sequence())
    partie.lancer_enigme("seq")

    partie.appui_bouton(7)

    assert partie.prendre_evenements() == []


# --- Ouverture des étages ---


def test_l_etage_suivant_s_ouvre_quand_toutes_ses_salles_sont_resolues(partie):
    resoudre(partie, "e1_a")
    assert partie.etat()["etages_ouverts"] == [1]

    resoudre(partie, "e1_b")
    assert partie.etat()["etages_ouverts"] == [1, 2]


def test_les_salles_d_un_etage_se_font_dans_n_importe_quel_ordre(partie):
    resoudre(partie, "e1_b")
    resoudre(partie, "e1_a")
    assert partie.etat()["etages_ouverts"] == [1, 2]


def test_la_salle_tuto_ouvre_l_etage_1(horloge):
    partie = partie_de(
        horloge,
        Salle(id="tuto", etage=0, nom="Tuto", mecanique="factice"),
        Salle(id="e1_a", etage=1, nom="A", mecanique="factice"),
    )
    assert partie.etat()["etages_ouverts"] == [0]

    resoudre(partie, "tuto")
    assert partie.etat()["etages_ouverts"] == [0, 1]


# --- Victoire ---


def test_resoudre_la_salle_finale_gagne_la_partie(partie):
    for salle_id in ["e1_a", "e1_b", "e2_a", "e3_a", "finale"]:
        resoudre(partie, salle_id)

    etat = partie.etat()
    assert etat["statut"] == "gagnee"
    assert etat["etages_ouverts"] == [1, 2, 3, 4]
    assert partie.prendre_evenements()[-2:] == [
        {"type": "enigme_resolue", "salle": "finale"},
        {"type": "partie_terminee"},
    ]


def test_une_victoire_reste_acquise_quand_le_temps_passe(partie, horloge):
    for salle_id in ["e1_a", "e1_b", "e2_a", "e3_a", "finale"]:
        resoudre(partie, salle_id)
    horloge.avancer(hours=1)
    assert partie.etat()["statut"] == "gagnee"


# --- Timer et défaite ---


def test_la_partie_continue_juste_avant_la_fin(partie, horloge):
    horloge.avancer(minutes=44, seconds=59)
    assert partie.etat()["statut"] == "en_cours"


def test_defaite_a_l_heure_de_fin(partie, horloge):
    horloge.avancer(minutes=45)
    assert partie.etat()["statut"] == "perdue"


def test_la_defaite_est_diffusee_une_seule_fois_et_eteint_les_leds(partie, horloge):
    partie.prendre_commandes()
    horloge.avancer(minutes=45)

    partie.etat()
    partie.etat()

    assert partie.prendre_evenements() == [{"type": "partie_terminee"}]
    assert partie.prendre_commandes() == [EteindreTout()]


def test_la_defaite_annule_l_enigme_en_cours(partie, horloge):
    partie.lancer_enigme("e1_a")
    horloge.avancer(minutes=45)
    assert partie.etat()["enigme_en_cours"] is None


def test_une_validation_apres_la_fin_est_refusee(partie, horloge):
    partie.lancer_enigme("e1_a")
    horloge.avancer(minutes=46)

    assert partie.appui_bouton(1) is None
    assert partie.etat()["salles_resolues"] == []
    assert partie.etat()["statut"] == "perdue"


def test_lancer_une_enigme_apres_la_defaite_est_refuse(partie, horloge):
    horloge.avancer(minutes=45)
    with pytest.raises(ActionImpossible):
        partie.lancer_enigme("e1_a")


def test_le_tic_declare_la_defaite(partie, horloge):
    horloge.avancer(minutes=45)
    partie.tic()
    assert partie.statut == "perdue"


class MecaniqueChrono(Mecanique):
    """Mécanique de test, résolue au premier tic."""

    def appui_bouton(self, bouton: int) -> Reponse:
        return Reponse()

    def tic(self, maintenant: datetime) -> Reponse:
        return Reponse(resolue=True)


def test_le_tic_est_transmis_a_l_enigme_en_cours(monkeypatch, horloge):
    monkeypatch.setitem(MECANIQUES, "chrono", MecaniqueChrono)
    partie = partie_de(
        horloge, Salle(id="chrono", etage=1, nom="C", mecanique="chrono")
    )
    partie.lancer_enigme("chrono")

    partie.tic()

    assert partie.etat()["salles_resolues"] == ["chrono"]


# --- Outils de test du simulateur ---


def test_resoudre_l_enigme_en_cours_sans_la_jouer(partie):
    partie.lancer_enigme("e1_a")
    partie.resoudre_enigme_en_cours()
    assert partie.etat()["salles_resolues"] == ["e1_a"]


def test_resoudre_sans_enigme_en_cours_est_refuse(partie):
    with pytest.raises(ActionImpossible):
        partie.resoudre_enigme_en_cours()


def test_declarer_la_defaite(partie):
    partie.prendre_evenements()
    partie.declarer_defaite()

    assert partie.etat()["statut"] == "perdue"
    assert partie.prendre_evenements() == [{"type": "partie_terminee"}]
    with pytest.raises(ActionImpossible):
        partie.declarer_defaite()
