from typing import Dict, Any

class SimpleMemory:
    def __init__(self):
        self.storage: Dict[str, Any] = {}

    def store(self, key: str, data: Any):
        self.storage[key] = data

    def retrieve(self, key: str) -> Any:
        return self.storage.get(key)

    def get_all(self) -> Dict[str, Any]:
        return self.storage