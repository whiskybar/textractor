import tempfile
from functools import lru_cache

import pytest
from httpx import AsyncClient
from pydantic import HttpUrl

from textractor.main import Definition, app, get_storage


@lru_cache()
def get_test_storage():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('{}')
    return get_storage(f.name)


app.dependency_overrides[get_storage] = get_test_storage


@pytest.mark.anyio
async def test_extract():
    definition = Definition(key='testkey', url='http://example.com', pattern='test')
    await get_test_storage().set(definition.key, definition.dict())
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f'/extract/{definition.key}')
    assert response.status_code == 200
    assert response.json() == definition.dict()


@pytest.mark.anyio
async def test_define():
    definition = Definition(key='testkey2', url='http://example.com', pattern='test2')
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f'/define/', json=definition.dict())
    assert response.status_code == 200
    assert await get_test_storage().get(definition.key) == definition.dict()
