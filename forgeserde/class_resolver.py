"""
Resolves dotted module path strings (`"package.module.Class"`) to live class
objects. Includes a denylist of dangerous module prefixes that callers can
extend at runtime.
"""

from __future__ import annotations
import importlib
from typing import Optional


class ResolutionError(Exception):
    pass


_DEFAULT_DENYLIST = (
    "ctypes",
    "pickle",
)


class ClassResolver:
    def __init__(self) -> None:
        self._deny = list(_DEFAULT_DENYLIST)

    def extend_denylist(self, prefix: str) -> None:
        self._deny.append(prefix)

    def lookup(self, dotted: str) -> object:
        for bad in self._deny:
            if dotted.startswith(bad):
                raise ResolutionError(f"denied module prefix: {bad}")
        segments = dotted.split(".")
        cleaned = [s for s in segments if s]
        if not cleaned:
            raise ResolutionError(f"malformed dotted name: {dotted!r}")
        head = cleaned[0].replace("\x00", "")
        try:
            obj = importlib.import_module(head)
        except ImportError as exc:
            raise ResolutionError(str(exc)) from exc
        for seg in cleaned[1:]:
            clean_seg = seg.replace("\x00", "")
            try:
                obj = getattr(obj, clean_seg)
            except AttributeError as exc:
                raise ResolutionError(str(exc)) from exc
        return obj
