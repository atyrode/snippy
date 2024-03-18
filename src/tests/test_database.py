import pytest

from ..database import DbManager

@pytest.fixture
def db_manager():
    # Using an in-memory SQLite database for testing
    db_url = "sqlite:///:memory:"
    manager = DbManager(db_url)
    return manager

def test_insert_value(db_manager):
    with db_manager as db:
        link_id = db.insert_value("https://example.com")
        assert isinstance(link_id, int)
        
def test_get_value(db_manager):
    with db_manager as db:
        link_id = db.insert_value("https://example.com")
        value, clicks = db.get_value(link_id)
        assert value == "https://example.com"
        assert clicks == 0

def test_increment_clicks(db_manager):
    with db_manager as db:
        link_id = db.insert_value("https://example.com")
        db.increment_clicks(link_id)
        _, clicks = db.get_value(link_id)
        assert clicks == 1

def test_get_value_invalid_id(db_manager):
    with db_manager as db:
        result = db.get_value(999)  # Assuming 999 is an ID that does not exist
        assert result is None