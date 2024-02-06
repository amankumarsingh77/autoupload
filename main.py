from typing import Optional
from uploadTV import upload_serie_from_watchasian
from fastapi import FastAPI
import os
import uvicorn

app = FastAPI()


@app.get("/")
async def home(url: Optional[str] = None):
    if url:
        return {"status": await upload_serie_from_watchasian(url)}
    return {"msg": "hi"}
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081)
