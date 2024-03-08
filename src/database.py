import sqlite3

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from typing import Optional, Tuple

Base = declarative_base()

class Link(Base):
    __tablename__ = 'links'
    
    id = Column(Integer, primary_key=True)
    value = Column(String, nullable=False)
    clicks = Column(Integer, default=0)
    
    
class DbManager:
    """Generic database class to handle sqlite3 database operations.

    `__enter__` and `__exit__` methods are used to handle the connection
    to the database and to close it when the context manager is exited.
    
    Using the `with` statement, the connection to the database will be
    automatically closed when the block is exited. And if an exception
    occurs, the transaction will be rolled back.
    

    Args:
        db_path (str): Path to the database file.
    """
    
    def __init__(self, db_url: str) -> None:
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
    
    def __enter__(self) -> Session:
        self.session = self.Session()
        return self

    def __exit__(self, ext_type, exc_value, traceback) -> None:
        self.Session.remove()
        if exc_value:
            self.session.rollback()
        else:
            self.session.commit()

    def exec_commit(self, instance) -> None:
        self.session.add(instance)
        self.session.commit()
    
    def exec_get(self, query, all: bool = False):
        if all:
            return query(self.session).all()
        return query(self.session).first()
        
    def insert_value(self, value: str) -> int:
        """Inserts a new URL or text value in the database and returns the row ID"""

        new_link = Link(value=value)
        self.exec_commit(new_link)
        return new_link.id
    
    def increment_clicks(self, link_id: int) -> None:
        """Increments the number of clicks for a given shortened link ID."""
        
        link = self.session.query(Link).filter(Link.id == link_id).first()
        if link:
            link.clicks += 1
            self.session.commit()
                
    def get_value(self, link_id: int) -> Optional[Tuple]:
        """Returns an URL or text value from the database based on its id."""

        link = self.session.query(Link).filter(Link.id == link_id).first()
        if link:
            return link.value, link.clicks
        return None