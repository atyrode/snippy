import sqlite3
from typing import Optional, Type
from types import TracebackType

class DbManager:
    """Generic database class to handle sqlite3 database operations.

    `__enter__` and `__exit__` methods are used to handle the connection
    to the database and to close it when the context manager is exited.
    
    Using the `with` statement, the connection to the database will be
    automatically closed when the block is exited. And if an exception
    occurs, the transaction will be rolled back.
    
    The queries are protected against SQL injection by the `?` placeholder.
    
    Args:
        db_path (str): Path to the database file.
    """
    
    def __init__(self, db_path: str) -> None:
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
    
    def __enter__(self) -> 'DbManager':
        return self

    def __exit__(self, 
                 ext_type: Optional[Type[BaseException]],
                 exc_value: Optional[BaseException], 
                 traceback: Optional[TracebackType]
                 ) -> None:
        self.cursor.close()
        if isinstance(exc_value, Exception):
            self.rollback()
        else:
            self.commit()
        self.connection.close()
    
    def rollback(self) -> None:
        self.connection.rollback()
        
    def commit(self) -> None:
        self.connection.commit()
    
    def close(self) -> None:
        self.connection.close()

    def create_table(self, table_name: str, fields: tuple) -> None:
        formatted_fields = ', '.join(fields)
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({formatted_fields})")
        self.commit()

    def list_tables(self) -> list[Optional[tuple]]:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return self.cursor.fetchall()
    
    def insert(self, table_name: str, fields: tuple, values: tuple) -> None:
        placeholders = ', '.join(['?' for _ in values])
        sql = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({placeholders})"
        self.cursor.execute(sql, values)
        self.commit()

    def update(self, table_name: str, fields: tuple, values: tuple, condition: str, condition_values: tuple) -> None:
        set_clause = ', '.join([f"{field}=?" for field in fields])
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {condition}=?"
        self.cursor.execute(sql, values + condition_values)
        self.commit()

    def delete(self, table_name: str, condition: str, condition_values: tuple) -> None:
        sql = f"DELETE FROM {table_name} WHERE {condition}=?"
        self.cursor.execute(sql, condition_values)
        self.commit()

    def select(self, table_name: str, fields: tuple, condition: str, condition_values: tuple) -> list[Optional[tuple]]:
        fields_clause = ', '.join(fields)
        sql = f"SELECT {fields_clause} FROM {table_name} WHERE {condition}=?"
        self.cursor.execute(sql, condition_values)
        return self.cursor.fetchall()

