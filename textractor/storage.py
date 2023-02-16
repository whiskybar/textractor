import json
import os


class DiskStorage:
    def __init__(self, path):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                f.write('{}')

    async def get(self, key):
        with open(self.path, 'r') as f:
            return json.load(f)[key]

    async def set(self, key, value):
        with open(self.path, 'r+') as f:
            data = json.load(f)
            data[key] = value
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()


storage = DiskStorage('/tmp/storage.json')
