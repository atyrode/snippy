from fastapi.testclient import TestClient
from main import app

def test_boilerplate():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}
        
def test_boilerplate_incorrect_path():
    with TestClient(app) as client:
        response = client.get("/incorrect")
        assert response.status_code == 404
        assert response.json() == {"detail": "Not Found"}