from typing import Iterable, Iterator, Mapping, override

from flip.components.controller.instruction_set import InstructionSet
from flip.core import Error, Errorable


class ControlMapping(Mapping[str, int], Errorable):
    """Mapping from control names to control indices."""

    class Error(Error): ...

    class KeyError(Error, KeyError): ...

    def __init__(self, instruction_set: InstructionSet) -> None:
        self.__controls: Mapping[str, int] = {
            control: i for i, control in enumerate(sorted(instruction_set.controls))
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
    def __getitem__(self, control: str) -> int:
        try:
            return self.__controls[control]
        except KeyError as e:
            raise self._error(f"Control {control} not found.", self.KeyError) from e

    def encode_value(self, controls: Iterable[str]) -> int:
        value = 0
        for control in controls:
            value |= 1 << self[control]
        return value

    def decode_value(self, value: int) -> frozenset[str]:
        return frozenset(
            {control for control, index in self.items() if value & (1 << index)}
        )
