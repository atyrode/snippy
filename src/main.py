import os

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from charset import URLCharset
from codec import Codec
from database import SnippyDB

## CONSTANTS ##

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_PATH  = os.path.join(PROJECT_ROOT, 'src', 'static')
DB_PATH      = os.path.join(PROJECT_ROOT, 'src', 'snippy.db')

DOMAIN_NAME  = "vite.lol"

## CORE LOGIC ##

url_charset = URLCharset(numeric=True, lowercase_ascii=True,
                         uppercase_ascii=True, special=False)
codec       = Codec(charset=url_charset)
app         = FastAPI()

## API ENDPOINTS ##

@app.get("/")
def read_root() -> dict:
    return FileResponse(f"{STATIC_PATH}/index.html")

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
    
    with SnippyDB(DB_PATH) as db:
        row_count = db.get_row_count()
        
    unique_id: int = row_count + 1
    encoded_uid: str = codec.encode(unique_id)
    
    shortened_url: str = f"{DOMAIN_NAME}{encoded_uid}"
    
    with SnippyDB(DB_PATH) as db:
        db.insert_link(url)
    
    return {"shortened_url": shortened_url}


@app.get("/decode")
def decode_url(url: str) -> dict:
    """Decodes a short string to its original URL

    Args:
        url (str): The URL to decode

    Returns:
        dict: A JSON response containing the original URL and the number of clicks
    """
    
    if url.startswith(DOMAIN_NAME):
        url = url[len(DOMAIN_NAME):]
    
    if url == "":
        return {"error": "No URL provided"}
    elif url == "0": # There's no row id 0, so there can't be a shortened URL for it
        return {"original_url": "https://en.wikipedia.org/wiki/0#Computer_science", "clicks": -1}
    elif url_charset.validate(url) == False:
        return {"error": "Not a valid URL"}
    
    decoded_id: int = codec.decode(url)
    with SnippyDB(DB_PATH) as db:
        result = db.select_link(decoded_id)
    
    if not isinstance(result, tuple):
        return {"error": "Not a valid URL"}
    else:
        original_url, clicks = result
    
    return {"original_url": original_url, "clicks": clicks}

@app.get("redirect?url={url}")
@app.get("/{url}")
@app.get(f"/{DOMAIN_NAME}" + "/{url}")
def redirect_url(url: str) -> dict:
    """Redirects the user to the original URL from the shortened string

    Args:
        url (str): The short string to decode and redirect to
    """
    
    decode_result = decode_url(url)
    
    if "error" in decode_result.keys():
        return decode_result
    
    original_url = decode_result["original_url"]
        
    with SnippyDB(DB_PATH) as db:
        db.increment_clicks(original_url)
        
    return RedirectResponse(original_url)

if __name__ == "__main__":
    
    # Create the database if it doesn't exist and the links table
    with SnippyDB(DB_PATH) as db:
        db.create_table(db.table_name, db.fields)
    
    # "/static/" avoids collisions with a possible /static generated path in the future
    app.mount("/static/", StaticFiles(directory=STATIC_PATH), name="static")

    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)