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
DB_PATH      = os.path.join(PROJECT_ROOT, 'snippy.db')

DOMAIN_NAME  = "snip.py/"

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
    
    print(f"Received encode URL: {url}")
    
    if url == "":
        return {"error": "No URL provided"}
    
    with SnippyDB(DB_PATH) as db:
        row_count = db.get_row_count()
        
    unique_id: int = row_count + 1
    encoded_uid: str = codec.encode(unique_id)
    
    shortened_url: str = f"{DOMAIN_NAME}{encoded_uid}"
    
    with SnippyDB(DB_PATH) as db:
        db.insert_link(url)
    
    return {"url": shortened_url}


@app.get("/decode")
def decode_url(url: str) -> dict:
    """Decodes a short string to its original URL

    Args:
        url (str): The URL to decode

    Returns:
        dict: A JSON response containing the original URL and the number of clicks
    """
    
    print(f"Received decode URL: {url}")
    
    if url.startswith(DOMAIN_NAME):
        url = url[len(DOMAIN_NAME):]
    
    if url == "":
        return {"error": "No URL provided"}
    elif url == "0": # There's no row id 0, so there can't be a shortened URL for it
        return {"url": "https://en.wikipedia.org/wiki/0#Computer_science", "clicks": -1}
    elif url_charset.validate(url) == False:
        return {"error": "Not a valid URL"}
    
    decoded_id: int = codec.decode(url)
    with SnippyDB(DB_PATH) as db:
        result = db.select_link(decoded_id)
    
    if not isinstance(result, tuple):
        return {"error": "Not a valid URL"}
    else:
        original_url, clicks = result
    
    return {"url": original_url, "clicks": clicks}

@app.get("/determine")
def determine_what_to_do(url: str):
    """Determines if the URL is a shortened one or a regular one
    
    Args:
        url (str): The URL to determine
    
    Returns:
        dict: A JSON response containing the original URL or the shortened one
    """
    
    print(f"Received determine URL: {url}")
    
    if url.startswith(DOMAIN_NAME) or url.startswith(f"http://{DOMAIN_NAME}"):
        return RedirectResponse(f"/decode?url={url}")
    else:
        return RedirectResponse(f"/encode?url={url}")
    
@app.get("/redirect/")
@app.get("/{url}")
@app.get(f"/{DOMAIN_NAME}" + "{url}")
def redirect_url(url: str) -> dict:
    """Redirects the user to the original URL from the shortened string

    Args:
        url (str): The short string to decode and redirect to
    """
    
    decode_result = decode_url(url)
    
    if "error" in decode_result.keys():
        return decode_result
    
    original_url = decode_result["url"]
        
    with SnippyDB(DB_PATH) as db:
        db.increment_clicks(original_url)
    
    if not original_url.startswith("http"):
        original_url = "http://" + original_url
        
    return RedirectResponse(original_url)
    
if __name__ == "__main__":
    
    # Create the database if it doesn't exist and the links table
    with SnippyDB(DB_PATH) as db:
        db.create_table(db.table_name, db.fields)
    
    # "/static/" avoids collisions with a possible /static generated path in the future
    app.mount("/static/", StaticFiles(directory=STATIC_PATH), name="static")

    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8080)