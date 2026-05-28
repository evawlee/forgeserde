"""
DynamicSerializer handles arbitrary Python types via type registration. It
serves as the contrast surface for ReduceSerializer in forgeserde tests: this
serializer threads the policy through every hook at the natural call site.
"""

from __future__ import annotations
from typing import Any, Optional

from forgeserde.policy import DeserializationPolicy, PolicyError
from forgeserde.class_resolver import ClassResolver


class DynamicSerializer:
    def __init__(self, resolver: ClassResolver, policy: Optional[DeserializationPolicy]) -> None:
        self._resolver = resolver
        self._policy = policy

    def dumps(self, obj: Any) -> bytes:
        return repr(obj).encode("utf-8")

    def loads(self, payload: dict) -> Any:
        cls_name = payload.get("class")
        state = payload.get("state")
        cls = self._resolver.lookup(cls_name) if cls_name else None

        if cls is not None and self._policy is not None:
            sub = self._policy.validate_class(cls, is_local=False)
            if sub is not None:
                cls = sub

        if cls is None:
            return state

        obj = cls.__new__(cls) if isinstance(cls, type) else cls
        if state is not None and self._policy is not None:
            sub_state = self._policy.intercept_setstate(obj, state)
            if sub_state is not None:
                state = sub_state
        if state is not None and hasattr(obj, "__setstate__"):
            obj.__setstate__(state)
        return obj
