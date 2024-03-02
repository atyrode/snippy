from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root() -> dict:
    """Boilerplate FastAPI endpoint

    Returns:
        dict: A Hello World JSON response
    """
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)