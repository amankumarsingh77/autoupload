from typing import Optional
from uploadTV import upload_serie_from_watchasian
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def home(url:Optional[str]=None):
    if url:
        return {"status":await upload_serie_from_watchasian(url)}
    return {"msg":"hi"}
