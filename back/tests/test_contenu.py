import pytest

from app.contenu import ContenuInvalide, Document, charger_salles, lire_salles


def salle_json(id: str, etage: int, **autres) -> dict:
    """Une salle valide au format de content/salles.json, modifiable champ par champ."""
    return {"id": id, "etage": etage, "nom": id, "mecanique": "factice", **autres}


def contenu(*salles: dict) -> dict:
    return {"salles": list(salles)}


FINALE = salle_json("finale", 4)


def test_le_contenu_du_projet_est_valide():
    salles = charger_salles()
    assert sum(salle.est_finale for salle in salles.values()) == 1


def test_lire_des_salles():
    salles = lire_salles(contenu(salle_json("e1_a", 1), FINALE))

    assert list(salles) == ["e1_a", "finale"]
    assert salles["e1_a"].etage == 1
    assert salles["e1_a"].parametres == {}
    assert salles["finale"].est_finale


def test_lire_les_documents():
    doc = {"id": "rapport", "titre": "Rapport", "texte": "..."}
    salles = lire_salles(contenu(salle_json("e1_a", 1, documents=[doc]), FINALE))
    assert salles["e1_a"].documents == [
        Document(id="rapport", titre="Rapport", texte="...")
    ]


@pytest.mark.parametrize("donnees", [[], {}, {"salles": "pas une liste"}])
def test_forme_generale_invalide(donnees):
    with pytest.raises(ContenuInvalide):
        lire_salles(donnees)


def test_identifiant_en_double():
    with pytest.raises(ContenuInvalide, match="double"):
        lire_salles(contenu(salle_json("e1_a", 1), salle_json("e1_a", 2), FINALE))


@pytest.mark.parametrize("etage", [0, 5, "1"])
def test_etage_invalide(etage):
    with pytest.raises(ContenuInvalide, match="étage"):
        lire_salles(contenu(salle_json("e1_a", etage), FINALE))


def test_aucune_salle_finale():
    with pytest.raises(ContenuInvalide, match="exactement une"):
        lire_salles(contenu(salle_json("e1_a", 1)))


def test_deux_salles_finales():
    with pytest.raises(ContenuInvalide, match="exactement une"):
        lire_salles(contenu(FINALE, salle_json("finale_2", 4)))


def test_mecanique_inconnue():
    with pytest.raises(ContenuInvalide, match="mécanique inconnue"):
        lire_salles(contenu(salle_json("e1_a", 1, mecanique="nexiste_pas"), FINALE))


def test_champ_manquant():
    salle = salle_json("e1_a", 1)
    del salle["nom"]
    with pytest.raises(ContenuInvalide):
        lire_salles(contenu(salle, FINALE))


def test_fichier_absent(tmp_path):
    with pytest.raises(ContenuInvalide):
        charger_salles(tmp_path / "absent.json")


def test_json_mal_forme(tmp_path):
    fichier = tmp_path / "salles.json"
    fichier.write_text("{ pas du json", encoding="utf-8")
    with pytest.raises(ContenuInvalide):
        charger_salles(fichier)
