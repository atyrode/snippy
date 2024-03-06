import sqlite3
from dataclasses import dataclass, field
from typing import Optional, Type, Union, Tuple, List
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
        
    def exec_commit(self, query: str, params: tuple) -> None:
        """Executes and commits a SQL query."""
        
        self.cursor.execute(query, params)
        self.commit()
        
    def exec_get(self, query: str, params: tuple, all: bool) -> Union[Tuple, List[Tuple]]:
        """Executes and commits a SQL query, and returns the result."""
        
        self.cursor.execute(query, params)
        if all:
            return self.cursor.fetchall()
        return self.cursor.fetchone()

    def create_table(self, table_name: str, fields: dict) -> None:
        """Creates a table in the database if it doesn't exist based
        on a dictionary of fields and their types.
        """
        formatted_fields = ', '.join(
            [f"{name} {field_type}"
             for name, field_type
             in fields.items()]
        )
        
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({formatted_fields})"
        
        self.exec_commit(sql, params=tuple())

    def list_tables(self) -> list[Optional[tuple]]:
        sql = f"SELECT name FROM sqlite_master WHERE type='table'"
        
        result = self.exec_get(sql, params=tuple(), all=True)
        return result
    
    def insert(self, table_name: str, fields: tuple, values: tuple) -> None:
        placeholders = ', '.join('?' * len(values))
        
        sql = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({placeholders})"
        
        self.exec_commit(sql, params=values)

    def update(self, table_name: str, fields: tuple, values: tuple, conditions: tuple, condition_values: tuple) -> None:
        set_clause = ', '.join([f"{field}=?" for field in fields])
        
        sql = f"UPDATE {table_name} SET {set_clause}"
        
        if conditions:
            condition_clause = ' AND '.join([f"{condition}=?" for condition in conditions])
            sql += f" WHERE {condition_clause}"
        
        self.exec_commit(sql, params=values + condition_values)

    def delete(self, table_name: str, conditions: tuple, condition_values: tuple) -> None:
        condition_clause = ' AND '.join([f"{condition}=?" for condition in conditions])
        
        sql = f"DELETE FROM {table_name} WHERE {condition_clause}"
        
        self.exec_commit(sql, params=condition_values)

    def select(self, table_name: str, fields: tuple, conditions: tuple, condition_values: tuple, all: bool) -> Union[Tuple, List[Tuple]]:
        fields_clause = ', '.join(fields)
        
        sql = f"SELECT {fields_clause} FROM {table_name}"
        
        if conditions:
            condition_clause = ' AND '.join([f"{condition}=?" for condition in conditions])
            sql += f" WHERE {condition_clause}"
            
        result = self.exec_get(sql, params=condition_values, all=all)
        return result
    
class SnippyDB(DbManager):
    """Database manager for the Snippy application.
    
    This class extends the `DbManager` class and adds specific methods
    to handle the `links` table.
    """
    
    def __init__(self, db_path: str) -> None:
        super().__init__(db_path)
        self.table_name = "links"
        
        self.id_key = "id"
        self.url_key = "url"
        self.clicks_key = "clicks"
        
        self.fields = {
            f"{self.id_key}": "INTEGER PRIMARY KEY",
            f"{self.url_key}": "TEXT NOT NULL",
            f"{self.clicks_key}": "INTEGER DEFAULT 0"
        }
        
    def get_row_count(self) -> Optional[int]:
        """Returns the number of rows in the main table."""
        
        sql = f"SELECT COUNT(*) FROM {self.table_name}"
        
        result = self.exec_get(sql, params=tuple(), all=False)
        return None if result is None else result[0]
    
    def insert_link(self, url: str) -> None:
        """Inserts a new link in the database."""
        
        self.insert(self.table_name, 
                    fields=(self.url_key,), 
                    values=(url,))
        
    def increment_clicks(self, id: int) -> None:
        """Increments the number of clicks for a given link."""
        
        # TODO: It seems like we can't have proper SQL injection protection for
        # this usecase, using self.update passes the click+1 as a string
        sql = f"UPDATE {self.table_name} SET {self.clicks_key}={self.clicks_key}+1 WHERE {self.id_key}=?"

        self.exec_commit(sql, params=(id,))
        
    def select_link(self, id: int) -> Optional[Tuple]:
        """Returns a link from the database based on its id."""
        
        result = self.select(
            table_name = self.table_name, 
            fields     = (self.url_key, self.clicks_key), 
            conditions = (self.id_key,), 
            condition_values = (id,), 
            all        = False
        )
        
        return result

