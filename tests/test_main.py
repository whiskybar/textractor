import pytest
from httpx import AsyncClient

from textractor.main import Definition, app, get_storage
from textractor.storage import MemoryStorage


@pytest.fixture
def test_storage():
    return MemoryStorage()


@pytest.fixture
def anyio_backend():
    return 'asyncio'


pytestmark = pytest.mark.anyio


async def test_extract(fastapi_dep, test_storage):
    definition = Definition(key='testkey', url='http://example.com', pattern='test')
    with fastapi_dep(app).override({get_storage: test_storage}):
        await test_storage.set(definition.key, definition.dict())
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f'/extract/{definition.key}')
    assert response.status_code == 200
    assert response.json() == definition.dict()


async def test_define(fastapi_dep, test_storage):
    definition = Definition(key='testkey2', url='http://example.com', pattern='test2')
    with fastapi_dep(app).override({get_storage: test_storage}):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(f'/define/', json=definition.dict())
    assert response.status_code == 200
    assert await test_storage.get(definition.key) == definition.dict()
