from typing import List


class BufferError(Exception):
    pass


class WriteBuffer:
    def __init__(self) -> None:
        self._chunks: List[bytes] = []
        self._length = 0

    def write_bytes(self, data: bytes) -> int:
        if not isinstance(data, (bytes, bytearray)):
            raise BufferError("data must be bytes")
        chunk = bytes(data)
        self._chunks.append(chunk)
        self._length += len(chunk)
        return len(chunk)

    def write_uint32(self, value: int) -> int:
        if value < 0 or value > 0xFFFFFFFF:
            raise BufferError(f"uint32 out of range: {value}")
        return self.write_bytes(value.to_bytes(4, "big"))

    def length(self) -> int:
        return self._length

    def to_bytes(self) -> bytes:
        return b"".join(self._chunks)

    def reset(self) -> None:
        self._chunks.clear()
        self._length = 0


class ReadBuffer:
    def __init__(self, data: bytes) -> None:
        if not isinstance(data, (bytes, bytearray)):
            raise BufferError("data must be bytes")
        self._data = bytes(data)
        self._pos = 0

    def read_bytes(self, n: int) -> bytes:
        if n < 0:
            raise BufferError(f"negative read: {n}")
        if self._pos + n > len(self._data):
            raise BufferError("buffer underflow")
        out = self._data[self._pos:self._pos + n]
        self._pos += n
        return out

    def read_uint32(self) -> int:
        raw = self.read_bytes(4)
        return int.from_bytes(raw, "big")

    def remaining(self) -> int:
        return len(self._data) - self._pos

    def at_end(self) -> bool:
        return self._pos >= len(self._data)
