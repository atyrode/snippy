import os
from database import DbManager

# Re-define __exit__ method to remove the test DbManager file after the test
old_exit = DbManager.__exit__

def overload_exit(self, *args, **kwargs):
    old_exit(self, *args, **kwargs)
    os.remove("test.db")

DbManager.__exit__ = overload_exit
# End of re-definition
        
def test_context_manager():
    with DbManager('test.db') as db:
        assert db.connection is not None
        assert db.cursor is not None
        
    try:
        with DbManager('test.db') as db:
            raise Exception
    except Exception:
        assert Exception is not None

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
        db.create_table("test", ("id INTEGER", "name TEXT"))
        assert db.list_tables() == [("test",)]
    
def test_create_table():
    with DbManager('test.db') as db:
        db.create_table("test", ("id INTEGER", "name TEXT"))
        assert ("test", ) in db.list_tables()
        assert len(db.list_tables()) == 1
        
def test_insert():
    with DbManager('test.db') as db:
        db.create_table("test", ("id INTEGER", "name TEXT"))
        db.insert("test", ("id", "name"), (1, "test"))
        db.cursor.execute("SELECT * FROM test")
        assert db.cursor.fetchall() == [(1, "test")]
        
def test_insert_sql_injection():
    with DbManager('test.db') as db:
        db.create_table("test", ("id INTEGER", "name TEXT"))
        db.insert("test", ("id", "name"), (1, "test'); DROP TABLE test; --"))
        db.cursor.execute("SELECT * FROM test")
        assert db.cursor.fetchall() == [(1, "test'); DROP TABLE test; --")]
        
def test_update():
    with DbManager('test.db') as db:
        db.create_table("test", ("id INTEGER", "name TEXT"))
        db.insert("test", ("id", "name"), (1, "test"))
        db.update("test", ("name",), ("test2",), "id=?", (1,))
        db.cursor.execute("SELECT * FROM test")
        assert db.cursor.fetchall() == [(1, "test2")]
        
def test_delete():
    with DbManager('test.db') as db:
        db.create_table("test", ("id INTEGER", "name TEXT"))
        db.insert("test", ("id", "name"), (1, "test"))
        db.delete("test", "id=?", (1,))
        db.cursor.execute("SELECT * FROM test")
        assert db.cursor.fetchall() == []
        
def test_select():
    with DbManager('test.db') as db:
        db.create_table("test", ("id INTEGER", "name TEXT"))
        db.insert("test", ("id", "name"), (1, "test"))
        db.cursor.execute("SELECT * FROM test")
        assert db.cursor.fetchall() == [(1, "test")]