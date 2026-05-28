from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TypeDescriptor:
    type_id: int
    qualified_name: str
    is_reducible: bool
    is_primitive: bool = False
    field_names: List[str] = field(default_factory=list)


@dataclass
class FrameHeader:
    protocol_version: int
    payload_length: int
    flags: int = 0
    schema_id: Optional[str] = None


@dataclass
class EncodedRecord:
    type_id: int
    payload: bytes
    schema_id: Optional[str] = None
    flags: int = 0


def make_type_descriptor(type_id: int, qualified_name: str, is_reducible: bool = True) -> TypeDescriptor:
    return TypeDescriptor(
        type_id=int(type_id),
        qualified_name=str(qualified_name),
        is_reducible=bool(is_reducible),
    )


def describe(record: EncodedRecord) -> str:
    return f"type_id={record.type_id} bytes={len(record.payload)} flags={record.flags}"
