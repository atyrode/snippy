import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from .charset import URLCharset
from .codec import Codec
from .database import ViteDB

load_dotenv()

## CONSTANTS ##

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_PATH  = os.path.join(PROJECT_ROOT, 'src', 'static')
DB_PATH      = os.path.join(PROJECT_ROOT, 'data', 'vite.db')

if "VITE_PROTOCOL" not in os.environ or "VITE_HOST" not in os.environ:
    raise ValueError("Environment variables VITE_PROTOCOL and VITE_HOST are required in .env file at project root")

PROTOCOL     = os.environ["VITE_PROTOCOL"]
HOST         = os.environ["VITE_HOST"]

if not PROTOCOL or not HOST:
    raise ValueError("Environment variables VITE_PROTOCOL and VITE_HOST are required to be non empty strings in .env file at project root")

DOMAIN_NAME  = f"{PROTOCOL}://{HOST}/"
SHORT_URL    = HOST[8:] # without the https://

## CORE LOGIC ##

url_charset = URLCharset(numeric=True, lowercase_ascii=True,
                         uppercase_ascii=True, special=False)
codec       = Codec(charset=url_charset)
app         = FastAPI(docs_url="/docs/")

# Create the database if it doesn't exist and the links table
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
with ViteDB(DB_PATH) as db:
    db.create_table(db.table_name, db.fields)
    
# "/static/" avoids collisions with a possible /static generated path in the future
app.mount("/static/", StaticFiles(directory=STATIC_PATH), name="static")
    
## API ENDPOINTS ##

@app.get("/")
def read_root() -> dict:
    return FileResponse(f"{STATIC_PATH}/index.html")

@app.get("/encode")
def encode_value(value: str) -> dict:
    """Encodes an URL or text value to a shortened URL.

    Args:
        value (str): The URL or text to encode

    Returns:
        dict: A JSON response containing the encoded value in the 'url' key
    """
        
    if value == "":
        return {"error": "No URL or text provided"}
    
    with ViteDB(DB_PATH) as db:
        unique_id: int = db.insert_value(value)
        
    encoded_uid: str = codec.encode(unique_id)
    
    shortened_url: str = f"{DOMAIN_NAME}{encoded_uid}"
    
    return {"url": shortened_url}


@app.get("/decode")
def decode_url(url: str) -> dict:
    """Decodes a shortened URL to its original URL or text value.

    Args:
        url (str): The shortened URL to decode

    Returns:
        dict: A JSON response containing the original value as the 'value' key
        and the number of redirection on the shortened URL as the 'clicks' key
    """
    
    # We keep only the part after the domain name using a regex pattern
    unique_id = re.sub(rf"{DOMAIN_NAME}|{SHORT_URL}", "", url)

    if unique_id == "":
        return {"error": "No URL provided"}
    elif unique_id == "0": # There's no row id 0, so there can't be a shortened URL for it
        return {"value": "https://en.wikipedia.org/wiki/0#Computer_science", "clicks": -1}
    elif url_charset.validate(unique_id) == False:
        return {"error": "Not a valid URL"}
    
    decoded_uid: int = codec.decode(unique_id)
    
    with ViteDB(DB_PATH) as db:
        result = db.get_value(decoded_uid)
    
    if not isinstance(result, tuple):
        return {"error": "No such shortened URL found"}
    else:
        original_url, clicks = result
    
    return {"value": original_url, "clicks": clicks}

@app.get("/determine")
def determine_what_to_do(query: str) -> RedirectResponse:
    """Determines if the value is a shortened URL to decode or an URL/text value
    to decode.
    
    Args:
        value (str): The value to determine the action to take on
    
    Returns:
        dict: A JSON response of the /decode or /encode endpoint with their
        respective keys and values depending on the input value.
    """
    
    # Check if it looks like a shortened URL
    if query.startswith(DOMAIN_NAME) or query.startswith(SHORT_URL):
        return RedirectResponse(f"/decode?url={query}")
    else:
        return RedirectResponse(f"/encode?value={query}")
    
@app.get("/redirect/" + DOMAIN_NAME + "{url}")
@app.get("/redirect/" + SHORT_URL + "{url}")
@app.get("/redirect/{url}")
@app.get("/" + DOMAIN_NAME + "{url}")
@app.get("/" + SHORT_URL + "{url}")
@app.get("/{url}")
def redirect_url(url: str) -> RedirectResponse:
    """Redirects the user to the original URL or display the text computed 
    from the received shortened string.

    Args:
        url (str): The shortened url to decode and redirect to
        
    Returns:
        RedirectResponse: A RedirectResponse to the original URL or
        a display of the text value that was shortened.
    """
    
    decode_result = decode_url(url)
        
    if "error" in decode_result.keys():
        return decode_result
    
    original_url = decode_result["value"]
    
    is_url = codec.is_value_url(original_url)
    
    with ViteDB(DB_PATH) as db:
        decoded_id: int = codec.decode(url)
        db.increment_clicks(decoded_id)
        
    if not is_url:
        return RedirectResponse(f"/decode?url={url}")
    
    return RedirectResponse(original_url)
