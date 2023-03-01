import json
import os

from azure.cosmos.aio import CosmosClient


class Storage:
    async def get(self, key: str) -> dict:
        return {}

    async def set(self, key: str, value: dict) -> None:
        pass


class MemoryStorage(Storage):
    def __init__(self):
        self.data = {}

    async def get(self, key: str) -> dict:
        return self.data[key]

    async def set(self, key: str, value: dict) -> None:
        self.data[key] = value


class DiskStorage(Storage):
    def __init__(self, path):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                f.write('{}')

    async def get(self, key: str) -> dict:
        with open(self.path, 'r') as f:
            return json.load(f)[key]

    async def set(self, key: str, value: dict) -> None:
        with open(self.path, 'r+') as f:
            data = json.load(f)
            data[key] = value
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()


class AzureCosmosStorage(Storage):
    def __init__(self, host, master_key, database, container):
        self.client = CosmosClient(
            host, {'masterKey': master_key}, user_agent='CosmosDBPythonQuickstart', user_agent_overwrite=True
        )
        self.db = self.client.get_database_client(database)
        self.container = self.db.get_container_client(container)

    async def get(self, key: str) -> dict:
        return await self.container.read_item(item=key, partition_key=key)

    async def set(self, key: str, value: dict) -> None:
        await self.container.create_item(value)
