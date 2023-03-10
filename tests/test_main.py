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


@pytest.fixture
def non_mocked_hosts() -> list:
    return ['test']


async def test_extract(fastapi_dep, test_storage, httpx_mock):
    url = 'http://example.com'
    httpx_mock.add_response(url=url, text='<title>Example</title>')
    definition = Definition(key='testkey', url=url, pattern='title')
    with fastapi_dep(app).override({get_storage: test_storage}):
        await test_storage.set(definition.key, definition.dict())
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f'/extract/{definition.key}')
    assert response.status_code == 200
    assert response.text == '"Example"'


async def test_definition(fastapi_dep, test_storage):
    url = 'http://example.com'
    definition = Definition(key='testkey', url=url, pattern='title')
    await test_storage.set(definition.key, dict(definition.dict(), garbage='extra key'))
    with fastapi_dep(app).override({get_storage: test_storage}):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f'/definition/{definition.key}')
    assert response.status_code == 200
    assert response.json() == definition.dict()


async def test_define(fastapi_dep, test_storage):
    definition = Definition(key='testkey2', url='http://example.com', pattern='test2')
    with fastapi_dep(app).override({get_storage: test_storage}):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(f'/define/', json=definition.dict())
    assert response.status_code == 200
    assert await test_storage.get(definition.key) == definition.dict()
