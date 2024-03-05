import os
import random
import time
import pytest

from fastapi.testclient import TestClient

import main
main.DB_PATH = "test.db"
DB_PATH = main.DB_PATH

from main import app, DOMAIN_NAME, LINKS_TABLE, cut_domain_name, get_row_count
from database import DbManager

@pytest.fixture(autouse=True)
def run_around_tests():
    with DbManager(DB_PATH) as db:
        db.create_table(**LINKS_TABLE)
    yield
    os.remove(DB_PATH)
    
def test_db_created():
    assert os.path.exists(DB_PATH)

def test_created_links_table():
    with DbManager(DB_PATH) as db:
        assert ("links",) in db.list_tables()

def test_cut_domain_name():
    assert cut_domain_name(f"{DOMAIN_NAME}1") == "1"
    assert cut_domain_name(f"{DOMAIN_NAME}1/") == "1/"
    assert cut_domain_name(f"{DOMAIN_NAME}") == ""
    assert cut_domain_name(f"{DOMAIN_NAME}/") == "/"
    
    random.seed(time.time())
    rand_string = "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(10))
    assert cut_domain_name(f"{DOMAIN_NAME}" + rand_string) == rand_string

def test_get_row_count():
    with DbManager(DB_PATH) as db:
        assert db.cursor.execute(f"SELECT COUNT(*) FROM links").fetchone()[0] == get_row_count()

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

def test_empty_url():
    with TestClient(app) as client:
        response = client.get("/encode?url=")
        assert response.status_code == 200
        assert response.json() == {"error": "No URL provided"}
        
    with TestClient(app) as client:
        response = client.get("/decode?url=")
        assert response.status_code == 200
        assert response.json() == {"error": "No URL provided"}

def test_encode():
    with TestClient(app) as client:
        response = client.get("/encode?url=https://www.wikipedia.org/")
        assert response.status_code == 200
        response = response.json()
        assert "shortened_url" in response
        assert DOMAIN_NAME in response["shortened_url"]
        assert len(response["shortened_url"].replace(DOMAIN_NAME, "")) > 0
        
def test_decode():
    with TestClient(app) as client:
        response = client.get("/encode?url=https://www.wikipedia.org/")
        shortened_url = response.json()["shortened_url"]
        
    with TestClient(app) as client:
        response = client.get(f"/decode?url={shortened_url}")
        assert response.status_code == 200
        response = response.json()
        assert "original_url" in response
        assert response["original_url"] == "https://www.wikipedia.org/"
        assert "clicks" in response
        assert response["clicks"] == 0
        
def test_decode_0():
    with TestClient(app) as client:
        response = client.get("/decode?url=" + DOMAIN_NAME + "0")
        assert response.status_code == 200
        response = response.json()
        assert "original_url" in response
        assert response["original_url"] == "https://en.wikipedia.org/wiki/0#Computer_science"
        assert "clicks" in response
        assert response["clicks"] == -1

def test_decode_invalid_url():
    with TestClient(app) as client:
        response = client.get("/decode?url=$")
        assert response.status_code == 200
        assert response.json() == {"error": "Not a valid snippy URL"}
        
def test_decode_not_found():
    with TestClient(app) as client:
        response = client.get("/decode?url=" + DOMAIN_NAME + "1")
        assert response.status_code == 404
        assert response.json() == {"detail": "URL not found"}