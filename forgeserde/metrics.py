from typing import Dict, List, Tuple


class EncodeMetrics:
    def __init__(self) -> None:
        self._counts: Dict[str, int] = {}
        self._bytes: Dict[str, int] = {}

    def record_encode(self, type_name: str, byte_size: int) -> None:
        self._counts[type_name] = self._counts.get(type_name, 0) + 1
        self._bytes[type_name] = self._bytes.get(type_name, 0) + byte_size

    def record_decode(self, type_name: str, byte_size: int) -> None:
        key = f"decode:{type_name}"
        self._counts[key] = self._counts.get(key, 0) + 1
        self._bytes[key] = self._bytes.get(key, 0) + byte_size

    def count_for(self, type_name: str) -> int:
        return self._counts.get(type_name, 0)

    def total_bytes_for(self, type_name: str) -> int:
        return self._bytes.get(type_name, 0)

    def summary(self) -> List[Tuple[str, int, int]]:
        rows: List[Tuple[str, int, int]] = []
        for k in sorted(self._counts.keys()):
            rows.append((k, self._counts[k], self._bytes.get(k, 0)))
        return rows

    def reset(self) -> None:
        self._counts.clear()
        self._bytes.clear()
