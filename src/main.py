import os

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

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

DOMAIN_NAME = "vite.lol"

@app.get("/")
def read_root() -> dict:
    # Shows the index.html file:
    return FileResponse("static/index.html")

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
    
    url: str = cut_domain_name(url) 
    
    if url == "":
        return {"error": "No URL provided"}
    # There is no row with id 0, so there can't be a shortened URL for it
    elif url == "0":
        return {"original_url": "https://en.wikipedia.org/wiki/0#Computer_science", "clicks": -1}
    
    try:
        url_charset.validate(url)
    except ValueError as e:
        return {"error": "Not a valid snippy URL"}
    
    decoded_id: int = codec.decode(url)
    
    print(decoded_id)
    
    with DbManager(DB_PATH) as db:
        result = db.select("links", ("url", "clicks",), "id", (decoded_id,))[0]
    
    if result is None:
        raise HTTPException(status_code=404, detail="URL not found")
    
    return {"original_url": result[0], "clicks": result[1]}

@app.get("redirect?url={url}")
@app.get("/{url}")
@app.get("/" + DOMAIN_NAME + "/{url}")
def redirect_url(url: str) -> dict:
    """Redirects the user to the original URL from the shortened string

    Args:
        url (str): The short string to decode

    Returns:
        dict: A JSON response containing the original URL
    """
    
    decode_result = decode_url(url)
    
    if "error" in decode_result.keys():
        return decode_result
    
    original_url = decode_result["original_url"]
        
    with DbManager(DB_PATH) as db:
        # Increment the clicks counter
        db.update("links", ("clicks",), "clicks+1", "url", (original_url,))
        
    return RedirectResponse(original_url)

if __name__ == "__main__":
    # Create the database and the table if they don't exist
    with DbManager(DB_PATH) as db:
        db.create_table(**LINKS_TABLE)
    
    # This avoids collisions with a possible /static path in the future
    app.mount("/static/", StaticFiles(directory="static"), name="static")

    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)