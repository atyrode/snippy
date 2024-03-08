import os
import pytest

from fastapi.testclient import TestClient

import src.api as api

api.DB_PATH = "test.db"
DB_PATH = api.DB_PATH

from src.api import app, DOMAIN_NAME, SHORT_URL
from database import ViteDB

@pytest.fixture(autouse=True)
def run_around_tests():
    with ViteDB(DB_PATH) as db: # Creates the test database
        db.create_table(db.table_name, db.fields)
    yield
    os.remove(DB_PATH)
    
def test_ensure_protocol():
    assert api.PROTOCOL != ""

def test_ensure_host():
    assert api.HOST != ""
    
def test_db_created():
    assert os.path.exists(DB_PATH)

def test_created_links_table():
    with ViteDB(DB_PATH) as db:
        assert ("links",) in db.list_tables()

def test_boilerplate():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
        
def test_boilerplate_incorrect_path():
    with TestClient(app) as client:
        response = client.get("/incorrect/path")
        assert response.status_code == 404
        assert response.json() == {"detail": "Not Found"}

def test_empty_url():
    with TestClient(app) as client:
        response = client.get("/encode?value=")
        assert response.status_code == 200
        assert response.json() == {"error": "No URL or text provided"}
        
    with TestClient(app) as client:
        response = client.get("/decode?url=")
        assert response.status_code == 200
        assert response.json() == {"error": "No URL provided"}

def test_encode():
    with TestClient(app) as client:
        response = client.get("/encode?value=https://www.wikipedia.org/")
        assert response.status_code == 200
        response = response.json()
        assert "url" in response
        assert DOMAIN_NAME in response["url"]
        assert len(response["url"].replace(DOMAIN_NAME, "")) > 0

def test_encode_no_value_argument():
    with TestClient(app) as client:
        response = client.get("/encode")
        assert response.status_code == 422
          
def test_decode():
    with TestClient(app) as client:
        response = client.get("/encode?value=https://www.wikipedia.org/")
        shortened_url = response.json()["url"]
        response = client.get(f"/decode?url={shortened_url}")
        assert response.status_code == 200
        response = response.json()
        assert "value" in response
        assert response["value"] == "https://www.wikipedia.org/"
        assert "clicks" in response
        assert response["clicks"] == 0

def test_decode_no_url_argument():
    with TestClient(app) as client:
        response = client.get("/decode")
        assert response.status_code == 422
        
def test_decode_0():
    with TestClient(app) as client:
        response = client.get("/decode?url=" + DOMAIN_NAME + "0")
        assert response.status_code == 200
        response = response.json()
        assert "value" in response
        assert response["value"] == "https://en.wikipedia.org/wiki/0#Computer_science"
        assert "clicks" in response
        assert response["clicks"] == -1

def test_decode_invalid_url():
    with TestClient(app) as client:
        response = client.get("/decode?url=$")
        assert response.status_code == 200
        assert response.json() == {"error": "Not a valid URL"}
        
def test_decode_not_found():
    with TestClient(app) as client:
        response = client.get("/decode?url=" + DOMAIN_NAME + "1")
        assert response.status_code == 200
        assert response.json() == {"error": "No such shortened URL found"}
        
def test_determine_is_encode():
    with TestClient(app) as client:
        response = client.get("/determine?query=https://www.wikipedia.org/")
        assert response.status_code == 200
        response = response.json()
        assert "url" in response
        assert DOMAIN_NAME in response["url"]
        assert len(response["url"].replace(DOMAIN_NAME, "")) > 0
        
def test_determine_is_decode():
    with TestClient(app) as client:
        response = client.get("/encode?value=https://www.wikipedia.org/")

        response = client.get(f"/determine?query={SHORT_URL}1")
        assert response.status_code == 200
        response = response.json()
        assert "value" in response
        assert response["value"] == "https://www.wikipedia.org/"
        assert "clicks" in response
        assert response["clicks"] == 0

        response = client.get(f"/determine?query={DOMAIN_NAME}1")
        assert response.status_code == 200
        response = response.json()
        assert "value" in response
        assert response["value"] == "https://www.wikipedia.org/"
        assert "clicks" in response
        assert response["clicks"] == 0
        
def test_determine_fail_encode():
    with TestClient(app) as client:
        response = client.get("/determine?query=")
        assert response.status_code == 200
        assert response.json() == {"error": "No URL or text provided"}
        
def test_determine_fail_decode():
    with TestClient(app) as client:
        response = client.get("/determine?query=" + DOMAIN_NAME + "1")
        assert response.status_code == 200
        assert response.json() == {"error": "No such shortened URL found"}
        
def test_redirect_is_url():
    with TestClient(app) as client:
        response = client.get("/encode?value=https://www.wikipedia.org/")
        shortened_url = response.json()["url"]
        response = client.get(f"/redirect/{shortened_url}")
        assert response.status_code == 200
        
        response = client.get(f"/{shortened_url}")
        assert response.status_code == 200

def test_redirect_is_text():
    with TestClient(app) as client:
        response = client.get("/encode?value=Hello World!")
        shortened_url = response.json()["url"]
        response = client.get(f"/redirect/{shortened_url}")
        assert response.status_code == 200
        
        response = client.get(f"/{shortened_url}")
        assert response.status_code == 200