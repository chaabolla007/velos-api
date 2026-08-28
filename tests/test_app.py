from app import app


def test_sante_repond_ok():
    client = app.test_client()
    reponse = client.get("/sante")

    assert reponse.status_code == 200
    assert reponse.get_json()["statut"] == "ok"


def test_alertes_sans_base(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    client = app.test_client()
    reponse = client.get("/alertes")
    donnees = reponse.get_json()

    assert reponse.status_code == 200
    assert donnees["source"] == "memoire"

    noms = {station["nom"] for station in donnees["alertes"]}
    assert noms == {"Place du Marche", "Universite"}
