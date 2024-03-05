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
    "fields": ("id INTEGER PRIMARY KEY", "url TEXT NOT NULL", "clicks INTEGER DEFAULT 0")
}

DOMAIN_NAME = "http://snip.py/"

def get_row_count() -> int:
    with DbManager(DB_PATH) as db:
        return db.cursor.execute(f"SELECT COUNT(*) FROM {LINKS_TABLE['table_name']}").fetchone()[0]

def cut_domain_name(url: str) -> str:
    """Removes the domain name from the URL to get the variable part"""
    
    if url.startswith(DOMAIN_NAME):
        return url[len(DOMAIN_NAME):]
    
    return url

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
    
    if url == "":
        return {"error": "No URL provided"}
    
    unique_id: int = get_row_count() + 1
    
    encoded_uid: str = codec.encode(unique_id)
    shortened_url: str = f"{DOMAIN_NAME}{encoded_uid}"
    
    with DbManager(DB_PATH) as db:
        db.insert("links", ("url",), (url,))
    
    return {"shortened_url": shortened_url}


@app.get("/decode")
def decode_url(url: str) -> dict:
    """Decodes a short string to its original URL

    Args:
        url (str): The URL to decode

    Returns:
        dict: A JSON response containing the original URL and the number of clicks
    """
    
    if url == "":
        return {"error": "No URL provided"}
    
    url: str = cut_domain_name(url) 
    decoded_id: int = codec.decode(url)
    
    # There is no row with id 0, so there can't be a shortened URL for it
    if url == "0":
        return {"original_url": "https://en.wikipedia.org/wiki/0#Computer_science", "clicks": -1}
    
    with DbManager(DB_PATH) as db:
        url, clicks = db.cursor.execute("SELECT url, clicks FROM links WHERE id=?", (decoded_id,)).fetchone()
        
    return {"original_url": url, "clicks": clicks}

if __name__ == "__main__":
    db = DbManager(DB_PATH)
    
    # Creates the links table if it doesn't exist
    db.create_table(**LINKS_TABLE)
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)