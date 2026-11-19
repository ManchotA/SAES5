import pytest

from app.boitier import VERT, Allumer, Clignoter
from app.mecaniques.sequence import MecaniqueSequence

PALETTE = {"rouge": (255, 0, 0), "vert": (0, 200, 0), "bleu": (0, 0, 255)}
BOUTONS = {"1": "rouge", "2": "vert", "3": "bleu"}


def sequence(*etapes: list[str], erreur: dict | None = None) -> MecaniqueSequence:
    parametres = {"boutons": BOUTONS, "etapes": list(etapes) or [["rouge", "vert"]]}
    if erreur is not None:
        parametres["erreur"] = erreur
    return MecaniqueSequence(parametres, PALETTE)


def jouer(mecanique: MecaniqueSequence, *boutons: int):
    """Appuie sur plusieurs boutons et renvoie la dernière réponse."""
    for bouton in boutons:
        reponse = mecanique.appui_bouton(bouton)
    return reponse


# --- Déroulement ---


def test_au_lancement_chaque_bouton_s_allume_dans_sa_couleur():
    assert sequence().demarrer() == [
        Allumer(1, (255, 0, 0)),
        Allumer(2, (0, 200, 0)),
        Allumer(3, (0, 0, 255)),
    ]


def test_la_bonne_sequence_resout_l_enigme():
    reponse = jouer(sequence(["rouge", "vert"]), 1, 2)
    assert reponse.resolue
    assert reponse.commandes == [Allumer(b, VERT) for b in (1, 2, 3)]


def test_un_bouton_sans_couleur_est_ignore():
    mecanique = sequence(["rouge", "vert"])
    reponse = mecanique.appui_bouton(7)
    assert not reponse.resolue and reponse.commandes == []
    assert jouer(mecanique, 1, 2).resolue


def test_deux_boutons_de_la_meme_couleur_conviennent_tous_les_deux():
    mecanique = MecaniqueSequence(
        {"boutons": {"1": "rouge", "2": "rouge"}, "etapes": [["rouge", "rouge"]]},
        PALETTE,
    )
    assert jouer(mecanique, 2, 1).resolue


def test_une_etape_reussie_fait_clignoter_les_boutons_en_vert():
    mecanique = sequence(["rouge"], ["vert", "bleu"])

    reponse = mecanique.appui_bouton(1)

    assert not reponse.resolue
    assert reponse.commandes == [Clignoter(b, VERT, 400) for b in (1, 2, 3)]
    assert mecanique.etat_public()["etapes_reussies"] == 1
    assert jouer(mecanique, 2, 3).resolue


# --- Rien ne permet de deviner un appui juste ---


def test_un_bon_appui_ne_donne_aucun_retour():
    assert sequence(["rouge", "vert"]).appui_bouton(1).commandes == []


def test_un_mauvais_appui_ne_donne_aucun_retour():
    assert sequence(["rouge", "vert"]).appui_bouton(3).commandes == []


def test_l_avancement_visible_ne_change_pas_avec_un_appui_juste_ou_faux():
    mecanique = sequence(["rouge", "vert", "bleu"], ["vert"])
    avant = mecanique.etat_public()

    mecanique.appui_bouton(1)  # juste
    assert mecanique.etat_public() == avant
    mecanique.appui_bouton(3)  # faux
    assert mecanique.etat_public() == avant
    assert avant == {"etapes_reussies": 0, "nb_etapes": 2, "longueur_etape": 3}


# --- Erreurs ---


def test_par_defaut_une_erreur_fait_recommencer_l_etape_en_cours():
    mecanique = sequence(["rouge"], ["vert", "bleu"])
    jouer(mecanique, 1, 2, 1)  # étape 1 réussie, puis erreur dans l'étape 2

    assert mecanique.etat_public()["etapes_reussies"] == 1
    assert not mecanique.appui_bouton(3).resolue  # l'étape 2 a bien repris au début
    assert jouer(mecanique, 2, 3).resolue


def test_une_erreur_peut_faire_recommencer_toute_la_sequence():
    mecanique = sequence(["rouge"], ["vert", "bleu"], erreur={"recommencer": "tout"})
    jouer(mecanique, 1, 2, 1)

    assert mecanique.etat_public()["etapes_reussies"] == 0
    assert jouer(mecanique, 1, 2, 3).resolue


# --- Vérification des paramètres au chargement ---


def test_des_parametres_valides_sont_acceptes():
    MecaniqueSequence.verifier_parametres(
        {
            "boutons": BOUTONS,
            "etapes": [["rouge"], ["vert", "bleu"]],
            "erreur": {"recommencer": "tout"},
        },
        PALETTE,
    )


@pytest.mark.parametrize(
    "parametres",
    [
        {"etapes": [["rouge"]]},
        {"boutons": {}, "etapes": [["rouge"]]},
        {"boutons": {"0": "rouge"}, "etapes": [["rouge"]]},
        {"boutons": {"11": "rouge"}, "etapes": [["rouge"]]},
        {"boutons": {"a": "rouge"}, "etapes": [["rouge"]]},
        {"boutons": {"1": "violet"}, "etapes": [["violet"]]},
        {"boutons": {"1": ["rouge"]}, "etapes": [["rouge"]]},
        {"boutons": {"1": "rouge"}},
        {"boutons": {"1": "rouge"}, "etapes": []},
        {"boutons": {"1": "rouge"}, "etapes": [[]]},
        {"boutons": {"1": "rouge"}, "etapes": ["rouge"]},
        {"boutons": {"1": "rouge"}, "etapes": [["vert"]]},
        {"boutons": {"1": "rouge"}, "etapes": [["rouge"]], "erreur": "tout"},
        {
            "boutons": {"1": "rouge"},
            "etapes": [["rouge"]],
            "erreur": {"recommencer": "x"},
        },
        {
            "boutons": {"1": "rouge"},
            "etapes": [["rouge"]],
            "erreur": {"retour": "tout"},
        },
    ],
)
def test_des_parametres_invalides_sont_refuses(parametres):
    with pytest.raises((TypeError, ValueError)):
        MecaniqueSequence.verifier_parametres(parametres, PALETTE)
