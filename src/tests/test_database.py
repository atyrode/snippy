import os

import pytest

from database import DbManager, SnippyDB

@pytest.fixture(autouse=True)
def run_after_each_test():
    yield
    os.remove("test.db")
    
def test_context_manager():
    with DbManager('test.db') as db:
        assert db.connection is not None
        assert db.cursor is not None
        
def test_commit():
    with DbManager('test.db') as db:
        db.cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER, name TEXT)")
        db.cursor.execute("INSERT INTO test (id, name) VALUES (1, 'test')")
        db.commit()
        db.cursor.execute("SELECT * FROM test")
        assert db.cursor.fetchall() == [(1, 'test')]

def test_roll_back():
    with DbManager('test.db') as db:
        db.cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER, name TEXT)")
        db.cursor.execute("INSERT INTO test (id, name) VALUES (1, 'test')")
        db.rollback()
        db.cursor.execute("SELECT * FROM test")
        assert db.cursor.fetchall() == []
        
def test_list_tables():
    with DbManager('test.db') as db:
        assert db.list_tables() == []
    
    with DbManager('test.db') as db:
        db.create_table("test", {"id": "INTEGER", "name": "TEXT"})
        assert db.list_tables() == [("test",)]
    
def test_create_table():
    with DbManager('test.db') as db:
        db.create_table("test",  {"id": "INTEGER", "name": "TEXT"})
        assert ("test", ) in db.list_tables()
        assert len(db.list_tables()) == 1
        
def test_insert():
    with DbManager('test.db') as db:
        db.create_table("test",  {"id": "INTEGER", "name": "TEXT"})
        db.insert("test", ("id", "name"), (1, "test"))
        db.cursor.execute("SELECT * FROM test")
        assert db.cursor.fetchall() == [(1, "test")]

def test_insert_sql_injection():
    with DbManager('test.db') as db:
        db.create_table("test",  {"id": "INTEGER", "name": "TEXT"})
        db.insert("test", ("id", "name"), (1, "test'); DROP TABLE test; --"))
        db.cursor.execute("SELECT * FROM test")
        assert db.cursor.fetchall() == [(1, "test'); DROP TABLE test; --")]
 
def test_update():
    with DbManager('test.db') as db:
        db.create_table("test",  {"id": "INTEGER", "name": "TEXT"})
        db.insert("test", ("id", "name"), (1, "test"))
        db.update("test", ("name",), ("test2",), ("id",), (1,))
        db.cursor.execute("SELECT * FROM test")
        assert db.cursor.fetchall() == [(1, "test2")]

def test_select():
    with DbManager('test.db') as db:
        db.create_table("test",  {"id": "INTEGER", "name": "TEXT"})
        db.insert("test", ("id", "name"), (1, "test"))
        db.select("test", ("name",), ("id"), (1,))
        assert db.cursor.fetchall() == [(1, "test")]
        
def test_delete():
    with DbManager('test.db') as db:
        db.create_table("test",  {"id": "INTEGER", "name": "TEXT"})
        db.insert("test", ("id", "name"), (1, "test"))
        db.delete("test", ("id",), (1,))
        db.cursor.execute("SELECT * FROM test")
        assert db.cursor.fetchall() == []

def test_select():
    with DbManager('test.db') as db:
        db.create_table("test",  {"id": "INTEGER", "name": "TEXT"})
        db.insert("test", ("id", "name"), (1, "test"))
        db.cursor.execute("SELECT * FROM test")
        assert db.cursor.fetchall() == [(1, "test")]


# Tests for SnippyDB

def test_created_links_table():
    with SnippyDB('test.db') as db:
        db.create_table(db.table_name, db.fields)
        assert (db.table_name,) in db.list_tables()
        
def test_insert_link():
    with SnippyDB('test.db') as db:
        db.create_table(db.table_name, db.fields)
        db.insert_link("https://www.wikipedia.org/")
        db.cursor.execute("SELECT * FROM links")
        assert db.cursor.fetchall() == [(1, "https://www.wikipedia.org/", 0)]
        
def test_increment_clicks():
    with SnippyDB('test.db') as db:
        db.create_table(db.table_name, db.fields)
        db.insert_link("https://www.wikipedia.org/")
        db.increment_clicks(1)
        result = db.select_link(1)
        assert result == ("https://www.wikipedia.org/", 1)
        
def test_select_link():
    with SnippyDB('test.db') as db:
        db.create_table(db.table_name, db.fields)
        db.insert_link("https://www.wikipedia.org/")
        result = db.select_link(1)
        assert result == ("https://www.wikipedia.org/", 0)
        
def test_get_row_count():
    with SnippyDB('test.db') as db:
        db.create_table(db.table_name, db.fields)
        assert db.get_row_count() == 0
        db.insert_link("https://www.wikipedia.org/")
        assert db.get_row_count() == 1
        db.insert_link("https://www.wikipedia.org/")
        assert db.get_row_count() == 2
        db.delete("links", ("id",), (1,))
        assert db.get_row_count() == 1
        db.delete("links", ("id",), (2,))
        assert db.get_row_count() == 0