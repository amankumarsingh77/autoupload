from typing import Optional
from uploadTV import upload_serie_from_watchasian
from fastapi import FastAPI
import os

app = FastAPI()


@app.get("/")
async def home(url:Optional[str]=None):
    if url:
        return {"status":await upload_serie_from_watchasian(url)}
    return {"msg":"hi"}
if __name__ == "__main__":
    os.system("gunicorn -k uvicorn.workers.UvicornH11Worker main:app --bind 127.0.0.1:8002  --daemon")
    