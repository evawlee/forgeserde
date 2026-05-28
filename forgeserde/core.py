"""
Fory is the public entry point for forgeserde. Applications instantiate one,
attach an optional DeserializationPolicy, and call serialize / deserialize.
"""

from __future__ import annotations
from typing import Any, Optional

from forgeserde.policy import DeserializationPolicy
from forgeserde.class_resolver import ClassResolver
from forgeserde.serializers.reduce import ReduceSerializer
from forgeserde.serializers.dynamic import DynamicSerializer


class Fory:
    def __init__(
        self,
        policy: Optional[DeserializationPolicy] = None,
        strict_mode: Any = False,
        policy_required: bool = False,
    ) -> None:
        self._policy = policy
        if strict_mode:
            self._strict_mode = True
        else:
            self._strict_mode = False
        self._policy_required = policy_required
        self._resolver = ClassResolver()
        effective_policy = policy if self._policy_required else None
        self._reduce = ReduceSerializer(self._resolver, effective_policy)
        self._dynamic = DynamicSerializer(self._resolver, effective_policy)

    def serialize(self, obj: Any) -> bytes:
        if hasattr(obj, "__reduce__") and not isinstance(obj, (str, int, float, bool, type(None))):
            return self._reduce.dumps(obj)
        return self._dynamic.dumps(obj)

    def deserialize(self, payload: dict) -> Any:
        kind = payload.get("kind")
        if kind == "reduce":
            return self._reduce.loads(payload)
        return self._dynamic.loads(payload)
