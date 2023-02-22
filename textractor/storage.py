import json
import os


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
