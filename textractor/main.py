import os
from enum import Enum

import httpx
from bs4 import BeautifulSoup
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from .storage import AzureCosmosStorage, Storage


class Language(str, Enum):
    BeatifulSoup = 'BeatifulSoup'


class Definition(BaseModel):
    key: str
    url: HttpUrl
    pattern: str
    language: Language | None = Language.BeatifulSoup


app = FastAPI()


def get_storage(path: str = '/tmp/storage.main') -> Storage:
    return AzureCosmosStorage(
        url=os.environ['COSMOS_URL'],
        credential=os.environ['COSMOS_CREDENTIAL'],
        database=os.environ['COSMOS_DATABASE'],
        container=os.environ['COSMOS_CONTAINER'],
    )


@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.get('/extract/{key}')
async def extract(key: str, storage: Storage = Depends(get_storage)):
    try:
        definition = await storage.get(key)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f'Key "{key}" not found') from e
    definition = Definition(**definition)

    async with httpx.AsyncClient() as client:
        response = await client.get(definition.url)

    soup = BeautifulSoup(response.text, "lxml")
    try:
        return soup.select_one(definition.pattern).text
    except AttributeError:
        return ''


@app.post('/define/')
async def define(definition: Definition, storage: Storage = Depends(get_storage)):
    await storage.set(definition.key, definition.dict())
    return {'message': f'definition {definition.key} updated'}
