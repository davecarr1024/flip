from dataclasses import dataclass, replace
from typing import Iterable, Mapping, Optional, Self

from flip.bytes import Byte
from flip.components.controller.step import Step


@dataclass(frozen=True)
class Instruction:
    @dataclass(frozen=True)
    class StatusEntry:
        name: str
        value: bool

    name: str
    opcode: Byte
    _statuses: frozenset[StatusEntry]
    steps: tuple[Step, ...]

    def with_steps(self, steps: Iterable[Step]) -> Self:
        return replace(self, steps=tuple(steps))

    def with_header(self, header: Iterable[Step]) -> Self:
        return self.with_steps(tuple(header) + self.steps)

    def with_footer(self, footer: Iterable[Step]) -> Self:
        return self.with_steps(self.steps + tuple(footer))

    @classmethod
    def create(
        cls,
        name: str,
        opcode: Byte,
        steps: Iterable[Step],
        statuses: Optional[Mapping[str, bool]] = None,
    ) -> "Instruction":
        return cls(
            name=name,
            opcode=opcode,
            _statuses=(
                frozenset(
                    cls.StatusEntry(name, value) for name, value in statuses.items()
                )
                if statuses is not None
                else frozenset()
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
