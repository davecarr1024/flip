from typing import Iterator, Mapping, override

from flip.core import Error, Errorable
from flip.instructions import InstructionSet


class StatusMapping(Mapping[str, int], Errorable):
    """Mapping from status names to status indices."""

    class Error(Error): ...

    class KeyError(Error, KeyError): ...

    class ValueError(Error, ValueError): ...

    def __init__(self, instruction_set: InstructionSet) -> None:
        self.__controls: Mapping[str, int] = {
            status: i for i, status in enumerate(sorted(instruction_set.statuses))
        }

    @override
    def __repr__(self) -> str:
        return f"ControlMapping({dict(self)})"

    @override
    def __len__(self) -> int:
        return len(self.__controls)

    @override
    def __iter__(self) -> Iterator[str]:
        yield from self.__controls

    @override
    def __getitem__(self, status: str) -> int:
        try:
            return self.__controls[status]
        except KeyError as e:
            raise self._error(f"Status {status} not found.", self.KeyError) from e

    def encode_address(self, statuses: Mapping[str, bool]) -> int:
        address = 0
        for status, value in statuses.items():
            address |= int(value) << self[status]
        return address

    def decode_address(self, address: int) -> Mapping[str, bool]:
        return {status: bool(address & (1 << index)) for status, index in self.items()}
