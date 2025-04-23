from dataclasses import dataclass
from typing import Iterable, Mapping

from flip.bytes import Byte
from flip.components.controller.step import Step


@dataclass(frozen=True)
class Instruction:
    @dataclass(frozen=True)
    class StatusEntry:
        name: str
        value: bool

    opcode: Byte
    _statuses: frozenset[StatusEntry]
    steps: tuple[Step, ...]

    @classmethod
    def create(
        cls, opcode: Byte, statuses: Mapping[str, bool], steps: Iterable[Step]
    ) -> "Instruction":
        return cls(
            opcode=opcode,
            _statuses=frozenset(
                cls.StatusEntry(name, value) for name, value in statuses.items()
            ),
            steps=tuple(steps),
        )

    @property
    def statuses(self) -> Mapping[str, bool]:
        return {entry.name: entry.value for entry in self._statuses}

    @property
    def controls(self) -> frozenset[str]:
        """The set of all controls used by this instruction."""
        return frozenset[str]().union(*[step.controls for step in self.steps])
