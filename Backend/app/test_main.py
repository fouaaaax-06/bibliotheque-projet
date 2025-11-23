from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API de la Bibliothèque"}

# Tu peux ajouter d'autres tests ici (mocking de DB nécessaire pour tests avancés)