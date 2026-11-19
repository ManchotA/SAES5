import pytest

from app.contenu import ContenuInvalide, Document, charger_contenu, lire_contenu


def salle_json(id: str, etage: int, **autres) -> dict:
    """Une salle valide au format de content/salles.json, modifiable champ par champ."""
    return {"id": id, "etage": etage, "nom": id, "mecanique": "factice", **autres}


def contenu(*salles: dict, couleurs: object = None) -> dict:
    donnees = {"salles": list(salles)}
    if couleurs is not None:
        donnees["couleurs"] = couleurs
    return donnees


FINALE = salle_json("finale", 4)


def test_le_contenu_du_projet_est_valide():
    salles = charger_contenu().salles
    assert sum(salle.est_finale for salle in salles.values()) == 1


def test_lire_des_salles():
    salles = lire_contenu(contenu(salle_json("e1_a", 1), FINALE)).salles

    assert list(salles) == ["e1_a", "finale"]
    assert salles["e1_a"].etage == 1
    assert salles["e1_a"].parametres == {}
    assert salles["finale"].est_finale


def test_lire_la_palette_de_couleurs():
    lu = lire_contenu(contenu(FINALE, couleurs={"rouge": [255, 0, 0]}))
    assert lu.couleurs == {"rouge": (255, 0, 0)}


def test_lire_les_documents():
    doc = {"id": "rapport", "titre": "Rapport", "texte": "..."}
    salles = lire_contenu(
        contenu(salle_json("e1_a", 1, documents=[doc]), FINALE)
    ).salles
    assert salles["e1_a"].documents == [
        Document(id="rapport", titre="Rapport", texte="...")
    ]


def test_la_partie_publique_cache_la_mecanique_et_ses_parametres():
    doc = {"id": "rapport", "titre": "Rapport", "texte": "..."}
    salles = lire_contenu(
        contenu(salle_json("e1_a", 1, documents=[doc]), FINALE)
    ).salles
    assert salles["e1_a"].partie_publique() == {
        "id": "e1_a",
        "etage": 1,
        "nom": "e1_a",
        "documents": [doc],
    }


def test_la_salle_tuto_est_a_l_etage_0():
    salles = lire_contenu(contenu(salle_json("tuto", 0), FINALE)).salles
    assert salles["tuto"].etage == 0


@pytest.mark.parametrize("donnees", [[], {}, {"salles": "pas une liste"}])
def test_forme_generale_invalide(donnees):
    with pytest.raises(ContenuInvalide):
        lire_contenu(donnees)


@pytest.mark.parametrize(
    "couleurs",
    ["pas un objet", {"rouge": "rouge"}, {"rouge": [255, 0]}, {"rouge": [256, 0, 0]}],
)
def test_palette_invalide(couleurs):
    with pytest.raises(ContenuInvalide, match="ouleur"):
        lire_contenu(contenu(FINALE, couleurs=couleurs))


def test_identifiant_en_double():
    with pytest.raises(ContenuInvalide, match="double"):
        lire_contenu(contenu(salle_json("e1_a", 1), salle_json("e1_a", 2), FINALE))


@pytest.mark.parametrize("etage", [-1, 5, "1"])
def test_etage_invalide(etage):
    with pytest.raises(ContenuInvalide, match="étage"):
        lire_contenu(contenu(salle_json("e1_a", etage), FINALE))


def test_aucune_salle_finale():
    with pytest.raises(ContenuInvalide, match="exactement une"):
        lire_contenu(contenu(salle_json("e1_a", 1)))


def test_deux_salles_finales():
    with pytest.raises(ContenuInvalide, match="exactement une"):
        lire_contenu(contenu(FINALE, salle_json("finale_2", 4)))


def test_mecanique_inconnue():
    with pytest.raises(ContenuInvalide, match="mécanique inconnue"):
        lire_contenu(contenu(salle_json("e1_a", 1, mecanique="nexiste_pas"), FINALE))


def test_les_parametres_de_la_mecanique_sont_verifies():
    salle = salle_json(
        "e1_a", 1, mecanique="sequence", parametres={"etapes": [["rouge"]]}
    )
    with pytest.raises(ContenuInvalide, match="e1_a"):
        lire_contenu(contenu(salle, FINALE, couleurs={"rouge": [255, 0, 0]}))


def test_des_parametres_qui_ne_sont_pas_un_objet():
    with pytest.raises(ContenuInvalide, match="parametres"):
        lire_contenu(contenu(salle_json("e1_a", 1, parametres=[]), FINALE))


def test_champ_manquant():
    salle = salle_json("e1_a", 1)
    del salle["nom"]
    with pytest.raises(ContenuInvalide):
        lire_contenu(contenu(salle, FINALE))


def test_fichier_absent(tmp_path):
    with pytest.raises(ContenuInvalide):
        charger_contenu(tmp_path / "absent.json")


def test_json_mal_forme(tmp_path):
    fichier = tmp_path / "salles.json"
    fichier.write_text("{ pas du json", encoding="utf-8")
    with pytest.raises(ContenuInvalide):
        charger_contenu(fichier)
