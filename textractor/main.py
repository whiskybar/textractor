from enum import Enum

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from .storage import DiskStorage


class Language(str, Enum):
    BeatifulSoup = 'BeatifulSoup'


class Definition(BaseModel):
    key: str
    url: HttpUrl
    pattern: str
    language: Language | None = Language.BeatifulSoup


app = FastAPI()


def get_storage(path: str = '/tmp/storage.main') -> DiskStorage:
    return DiskStorage(path)


@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.get('/extract/{key}')
async def extract(key: str, storage: DiskStorage = Depends(get_storage)):
    try:
        return await storage.get(key)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f'Key "{key}" not found') from e


@app.post('/define/')
async def define(definition: Definition, storage: DiskStorage = Depends(get_storage)):
    await storage.set(definition.key, definition.dict())
    return {'message': f'definition {definition.key} updated'}
