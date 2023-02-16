from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .storage import storage


class Definition(BaseModel):
    key: str
    url: str
    pattern: str
    language: str | None = 'BeatifulSoup'


app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.get('/extract/{key}')
async def extract(key: str):
    try:
        return await storage.get(key)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f'Key "{key}" not found') from e


@app.post('/define/')
async def define(definition: Definition) -> str:
    await storage.set(definition.key, definition.dict())
    return {'message': f'definition {definition.key} updated'}
