from dataclasses import dataclass, field
from typing import Iterable, Iterator, Mapping, Sized, override

from flip.components.alu.operations.operation import Operation
from flip.core import Error, Errorable


@dataclass(frozen=True)
class OperationSet(Errorable, Sized, Iterable[Operation]):
    class Error(Error): ...

    class DuplicateOperationName(Error): ...

    class KeyError(Error, KeyError): ...

    _operations: frozenset[Operation] = field(default_factory=frozenset[Operation])

    def __post_init__(self) -> None:
        names = set[str]()
        for operation in self._operations:
            if operation.name in names:
                raise self._error(
                    f"Duplicate operation name {operation.name}.",
                    self.DuplicateOperationName,
                )
            names.add(operation.name)

    @classmethod
    def create(cls, operations: Iterable[Operation]) -> "OperationSet":
        return cls(_operations=frozenset(operations))

    @property
    def operations(self) -> Iterable[Operation]:
        return sorted(self._operations, key=lambda operation: operation.name)

    @property
    def operations_by_name(self) -> Mapping[str, Operation]:
        return {operation.name: operation for operation in self._operations}

    @property
    def operations_by_index(self) -> Mapping[int, Operation]:
        return dict(enumerate(self.operations))

    def operation_index(self, operation: Operation | str) -> int:
        if isinstance(operation, str):
            operation = self.operation(operation)
        try:
            return list(self.operations).index(operation)
        except ValueError as e:
            raise self._error(f"Operation {operation} not found.", self.KeyError) from e

    def operation(self, index: str | int) -> Operation:
        try:
            match index:
                case str():
                    return self.operations_by_name[index]
                case int():
                    return self.operations_by_index[index]
        except KeyError as e:
            raise self._error(f"Operation {index} not found.", self.KeyError) from e

    @override
    def __len__(self) -> int:
        return len(self._operations)

    @override
    def __iter__(self) -> Iterator[Operation]:
        yield from self.operations
