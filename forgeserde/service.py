from typing import Any, Dict, Optional

from .core import Fory
from .metrics import EncodeMetrics
from .type_registry import TypeRegistry
from .policy import DeserializationPolicy


class SerializationService:
    def __init__(self, policy: Optional[DeserializationPolicy] = None) -> None:
        self.fory = Fory(policy=policy)
        self.registry = TypeRegistry()
        self.metrics = EncodeMetrics()

    def encode(self, obj: Any) -> bytes:
        out = self.fory.serialize(obj)
        self.metrics.record_encode(type(obj).__name__, len(out))
        return out

    def decode(self, payload: Dict[str, Any]) -> Any:
        out = self.fory.deserialize(payload)
        size = len(repr(payload).encode("utf-8"))
        self.metrics.record_decode(type(out).__name__ if out is not None else "None", size)
        return out

    def metrics_snapshot(self) -> Dict[str, Any]:
        return {
            "by_type": self.metrics.summary(),
            "registered_types": self.registry.count(),
        }
