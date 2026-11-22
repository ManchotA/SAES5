"""Tests du serveur : routes REST, WebSocket des écrans et WebSocket du boîtier."""

import pytest
from fastapi.testclient import TestClient

from app.contenu import Contenu, Document, Salle
from app.main import creer_app
from app.partie import Partie

PALETTE = {"rouge": (255, 0, 0), "vert": (0, 200, 0)}
NOIR, ROUGE, VERT = [0, 0, 0], [255, 0, 0], [0, 200, 0]
TOUT_ETEINT = {"type": "leds", "couleurs": [NOIR] * 10}


def partie_de_test(horloge) -> Partie:
    """Une salle « séquence » en deux étapes (rouge, puis vert) et une finale factice."""
    salles = [
        Salle(
            id="e1_seq",
            etage=1,
            nom="Séquence",
            mecanique="sequence",
            parametres={
                "boutons": {"1": "rouge", "2": "vert"},
                "etapes": [["rouge"], ["vert"]],
            },
            documents=[Document(id="doc", titre="Titre", texte="Texte")],
        ),
        Salle(id="finale", etage=4, nom="Finale", mecanique="factice"),
    ]
    return Partie(Contenu(couleurs=PALETTE, salles={s.id: s for s in salles}), horloge)


@pytest.fixture
def client(horloge):
    """Serveur de test en mode développement (comme avec dev.bat)."""
    app = creer_app(partie_de_test(horloge), intervalle_timer=0.05, mode_dev=True)
    with TestClient(app) as client:
        yield client


@pytest.fixture
def client_expo(horloge):
    """Serveur de test hors développement (comme à l'exposition)."""
    app = creer_app(partie_de_test(horloge), intervalle_timer=0.05, mode_dev=False)
    with TestClient(app) as client:
        yield client


# --- Routes REST ---


def test_sante(client):
    assert client.get("/api/sante").json() == {"statut": "ok"}


def test_les_salles_ne_montrent_que_leur_partie_publique(client):
    assert client.get("/api/salles").json() == [
        {
            "id": "e1_seq",
            "etage": 1,
            "nom": "Séquence",
            "documents": [{"id": "doc", "titre": "Titre", "texte": "Texte"}],
        },
        {"id": "finale", "etage": 4, "nom": "Finale", "documents": []},
    ]


def test_nouvelle_partie(client):
    assert client.get("/api/partie").json()["statut"] == "aucune"

    etat = client.post("/api/partie").json()

    assert etat["statut"] == "en_cours"
    assert etat["fin_a"] == "2026-10-25T15:45:00"
    assert etat["etages_ouverts"] == [1]


def test_lancer_puis_annuler_une_enigme(client):
    client.post("/api/partie")

    etat = client.post("/api/partie/salles/e1_seq/enigme").json()
    assert etat["enigme_en_cours"] == "e1_seq"
    assert etat["enigme_etat"] == {
        "etapes_reussies": 0,
        "nb_etapes": 2,
        "longueur_etape": 1,
    }

    etat = client.delete("/api/partie/salles/e1_seq/enigme").json()
    assert etat["enigme_en_cours"] is None


def test_salle_inconnue(client):
    client.post("/api/partie")
    reponse = client.post("/api/partie/salles/nexiste_pas/enigme")
    assert reponse.status_code == 404
    assert "erreur" in reponse.json()


def test_action_impossible(client):
    client.post("/api/partie")
    reponse = client.post("/api/partie/salles/finale/enigme")
    assert reponse.status_code == 409
    assert "erreur" in reponse.json()


# --- WebSockets : partie jouée avec le simulateur ---


def test_une_enigme_jouee_sur_le_boitier(client):
    with (
        client.websocket_connect("/ws") as ecran,
        client.websocket_connect("/ws/boitier") as boitier,
    ):
        assert boitier.receive_json() == TOUT_ETEINT
        assert ecran.receive_json()["type"] == "boitier_reconnecte"

        client.post("/api/partie")
        assert boitier.receive_json() == TOUT_ETEINT

        client.post("/api/partie/salles/e1_seq/enigme")
        assert boitier.receive_json()["couleurs"][:3] == [ROUGE, VERT, NOIR]

        # Un mauvais appui n'envoie rien : le prochain message vient de l'appui suivant
        boitier.send_json({"type": "appui", "bouton": 2})

        boitier.send_json({"type": "appui", "bouton": 1})  # étape 1 réussie
        for bouton in (1, 2):
            assert boitier.receive_json() == {
                "type": "clignoter",
                "bouton": bouton,
                "couleur": VERT,
                "duree": 400,
            }
        progression = ecran.receive_json()
        assert progression["type"] == "enigme_progression"
        assert progression["partie"]["enigme_etat"]["etapes_reussies"] == 1

        boitier.send_json({"type": "appui", "bouton": 2})
        assert boitier.receive_json()["couleurs"][:2] == [VERT, VERT]
        resolue = ecran.receive_json()
        assert resolue["type"] == "enigme_resolue"
        assert resolue["salle"] == "e1_seq"
        assert resolue["partie"]["salles_resolues"] == ["e1_seq"]


def test_la_fin_du_temps_est_diffusee(client, horloge):
    with client.websocket_connect("/ws") as ecran:
        client.post("/api/partie")
        horloge.avancer(minutes=45)
        client.get("/api/partie")  # la tâche du timer l'aurait fait d'elle-même

        message = ecran.receive_json()
        assert message["type"] == "partie_terminee"
        assert message["partie"]["statut"] == "perdue"


def test_la_deconnexion_du_boitier_est_diffusee(client):
    with client.websocket_connect("/ws") as ecran:
        with client.websocket_connect("/ws/boitier") as boitier:
            boitier.receive_json()
            assert ecran.receive_json()["type"] == "boitier_reconnecte"
        assert ecran.receive_json()["type"] == "boitier_deconnecte"


def test_les_outils_de_test_du_simulateur(client):
    with (
        client.websocket_connect("/ws") as ecran,
        client.websocket_connect("/ws/boitier") as boitier,
    ):
        boitier.receive_json()
        ecran.receive_json()

        boitier.send_json({"type": "test", "action": "resoudre"})
        assert boitier.receive_json()["type"] == "erreur"

        client.post("/api/partie")
        boitier.receive_json()
        client.post("/api/partie/salles/e1_seq/enigme")
        boitier.receive_json()

        boitier.send_json({"type": "test", "action": "resoudre"})
        assert ecran.receive_json()["type"] == "enigme_resolue"

        boitier.send_json({"type": "test", "action": "perdre"})
        message = ecran.receive_json()
        assert message["type"] == "partie_terminee"
        assert message["partie"]["statut"] == "perdue"
        assert boitier.receive_json() == TOUT_ETEINT


def test_les_messages_inconnus_du_boitier_sont_ignores(client):
    with client.websocket_connect("/ws/boitier") as boitier:
        boitier.receive_json()
        boitier.send_text("pas du json")
        boitier.send_json({"type": "nimporte_quoi"})
        boitier.send_json({"type": "appui", "bouton": "un"})

        boitier.send_json({"type": "test", "action": "resoudre"})
        assert boitier.receive_json()["type"] == "erreur"


# --- Simulateur ---


def test_le_simulateur_est_servi(client):
    reponse = client.get("/simulateur/")
    assert reponse.status_code == 200
    assert "Simulateur du boîtier" in reponse.text
    assert client.get("/simulateur").status_code == 200
    assert client.get("/simulateur/widget.js").status_code == 200


def test_en_developpement_le_boitier_virtuel_est_visible_avec_ses_outils(client):
    assert client.get("/simulateur/reglages.json").json() == {
        "visible_par_defaut": True,
        "outils_de_test": True,
    }


def test_hors_developpement_le_boitier_virtuel_est_cache_sans_outils(client_expo):
    assert client_expo.get("/simulateur/reglages.json").json() == {
        "visible_par_defaut": False,
        "outils_de_test": False,
    }


def test_hors_developpement_les_raccourcis_de_test_sont_ignores(client_expo):
    with client_expo.websocket_connect("/ws/boitier") as boitier:
        boitier.receive_json()
        client_expo.post("/api/partie")
        boitier.receive_json()
        client_expo.post("/api/partie/salles/e1_seq/enigme")
        boitier.receive_json()

        boitier.send_json({"type": "test", "action": "resoudre"})  # ignoré
        boitier.send_json({"type": "appui", "bouton": 1})

        # L'énigme est toujours en cours : l'appui réussit sa première étape
        assert boitier.receive_json()["type"] == "clignoter"
        assert client_expo.get("/api/partie").json()["salles_resolues"] == []
