"""
Policy hook surface for forgeserde deserializers.

Library users subclass DeserializationPolicy and override one or more of the
three hook methods. Every serializer that touches user supplied bytes is
expected to thread its configured policy through these hooks at the natural
call sites.
"""

from __future__ import annotations
from typing import Any, Callable, Optional, Tuple


class PolicyError(Exception):
    pass


class DeserializationPolicy:
    """
    Override any subset of the three hooks. Returning a value other than None
    indicates the hook elected to substitute that value for the original
    operation; returning None means the operation should proceed unchanged.
    Raising signals a hard rejection.
    """

    def validate_class(self, cls: type, is_local: bool = False) -> Optional[type]:
        return None

    def intercept_reduce_call(self, callable_obj: Callable, args: Tuple[Any, ...]) -> Optional[Any]:
        return None

    def intercept_setstate(self, obj: Any, state: Any) -> Optional[Any]:
        return None
