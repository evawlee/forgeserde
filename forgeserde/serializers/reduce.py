"""
ReduceSerializer handles types that implement the __reduce__ / __setstate__
protocol. It resolves callables via the resolver, invokes the reducer with
the supplied arguments, and threads __setstate__ payloads into the
reconstructed object.
"""

from __future__ import annotations
from typing import Any, Optional, Tuple

from forgeserde.policy import DeserializationPolicy
from forgeserde.class_resolver import ClassResolver


class ReduceSerializer:
    def __init__(self, resolver: ClassResolver, policy: Optional[DeserializationPolicy]) -> None:
        self._resolver = resolver
        self._policy = policy

    def dumps(self, obj: Any) -> bytes:
        return repr(obj).encode("utf-8")

    def resolve_global_name(self, dotted: str) -> Any:
        return self._resolver.lookup(dotted)

    def _invoke_reducer(self, callable_obj: Any, args: Tuple[Any, ...]) -> Any:
        return callable_obj(*args)

    def restore_state(self, obj: Any, state: Any) -> Any:
        if hasattr(obj, "__setstate__"):
            obj.__setstate__(state)
        elif isinstance(state, dict):
            for k, v in state.items():
                try:
                    setattr(obj, k, v)
                except Exception:
                    pass
        return obj

    def loads(self, payload: dict) -> Any:
        cls_name = payload.get("callable")
        args = tuple(payload.get("args", ()))
        state = payload.get("state")

        callable_obj = self.resolve_global_name(cls_name) if cls_name else None
        if callable_obj is None:
            return None
        obj = self._invoke_reducer(callable_obj, args)
        if state is not None:
            self.restore_state(obj, state)
        return obj
