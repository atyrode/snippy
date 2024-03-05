import os

import uvicorn
from fastapi import FastAPI

from charset import URLCharset
from codec import Codec
from database import DbManager

url_charset = URLCharset(numeric=True, lowercase_ascii=True,
                         uppercase_ascii=True, special=False)
codec       = Codec(charset=url_charset)
app         = FastAPI()

PARENT_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH     = PARENT_DIR + "/snippy.db"
LINKS_TABLE = {
    "table_name": "links",
    "fields": ("id INTEGER PRIMARY KEY", "url TEXT NOT NULL")
}

DOMAIN_NAME = "snip.py"

def get_row_count() -> int:
    with DbManager(DB_PATH) as db:
        return db.cursor.execute("SELECT COUNT(*) FROM links").fetchone()[0]
    
@app.get("/")
def read_root() -> dict:
    """Boilerplate FastAPI endpoint

    Returns:
        dict: A Hello World JSON response
    """
    return {"Hello": "World"}

@app.get("/encode")
def encode_url(url: str) -> dict:
    """Encodes an URL to a short string

    Args:
        url (str): The URL to encode

    Returns:
        dict: A JSON response containing the encoded URL
    """
    
    unique_id: int = get_row_count()
    
    encoded_uid: str = codec.encode(unique_id)
    shortened_url: str = f"{DOMAIN_NAME}/{encoded_uid}"
    
    with DbManager(DB_PATH) as db:
        db.insert("links", ("url",), (url,))
    
    return {"shortened_url": shortened_url}

if __name__ == "__main__":
    db = DbManager(DB_PATH)
    
    # Creates the links table if it doesn't exist
    db.create_table(**LINKS_TABLE)
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)