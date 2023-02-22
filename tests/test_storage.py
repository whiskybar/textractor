import pytest

from textractor.storage import DiskStorage, MemoryStorage


@pytest.fixture
def anyio_backend():
    return 'asyncio'


pytestmark = pytest.mark.anyio


async def test_memory_storage():
    storage = MemoryStorage()
    with pytest.raises(KeyError):
        assert await storage.get('foo')
    await storage.set('foo', {'hello': 'world'})
    assert await storage.get('foo') == {'hello': 'world'}


async def test_disk_storage(tmp_path):
    storage = DiskStorage(tmp_path / 'storage')
    with pytest.raises(KeyError):
        assert await storage.get('foo')
    await storage.set('foo', {'hello': 'world'})
    assert await storage.get('foo') == {'hello': 'world'}
