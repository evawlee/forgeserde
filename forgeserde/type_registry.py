from typing import Dict, List, Optional

from .schemas import TypeDescriptor


class TypeRegistry:
    def __init__(self) -> None:
        self._by_id: Dict[int, TypeDescriptor] = {}
        self._by_name: Dict[str, TypeDescriptor] = {}
        self._next_id = 1000

    def register(self, descriptor: TypeDescriptor) -> TypeDescriptor:
        if descriptor.type_id in self._by_id:
            raise ValueError(f"type_id {descriptor.type_id} already registered")
        if descriptor.qualified_name in self._by_name:
            raise ValueError(f"name {descriptor.qualified_name} already registered")
        self._by_id[descriptor.type_id] = descriptor
        self._by_name[descriptor.qualified_name] = descriptor
        return descriptor

    def auto_register(self, qualified_name: str, is_reducible: bool = True) -> TypeDescriptor:
        if qualified_name in self._by_name:
            return self._by_name[qualified_name]
        descriptor = TypeDescriptor(
            type_id=self._next_id,
            qualified_name=qualified_name,
            is_reducible=is_reducible,
        )
        self._next_id += 1
        return self.register(descriptor)

    def get_by_id(self, type_id: int) -> Optional[TypeDescriptor]:
        return self._by_id.get(type_id)

    def get_by_name(self, qualified_name: str) -> Optional[TypeDescriptor]:
        return self._by_name.get(qualified_name)

    def count(self) -> int:
        return len(self._by_id)

    def list_names(self) -> List[str]:
        return sorted(self._by_name.keys())

    def clear(self) -> None:
        self._by_id.clear()
        self._by_name.clear()
        self._next_id = 1000
