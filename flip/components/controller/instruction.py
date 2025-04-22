from dataclasses import dataclass
from typing import Iterable, Iterator, Mapping, Sized, override

from flip.bytes import Byte
from flip.components.controller.step import Step


@dataclass(frozen=True)
class Instruction(Sized, Iterable[Step]):
    opcode: Byte
    statuses: Mapping[str, bool]
    _steps: list[Step]

    @override
    def __len__(self) -> int:
        return len(self.steps)

    @override
    def __iter__(self) -> Iterator[Step]:
        yield from self.steps

    @classmethod
    def _preamble(cls) -> list[Step]:
        raise NotImplementedError()

    @classmethod
    def _last_step_required_controls(cls) -> frozenset[str]:
        raise NotImplementedError()

    @property
    def steps(self) -> list[Step]:
        steps = self._preamble() + self._steps
        if steps:
            steps[-1] = steps[-1].with_controls(self._last_step_required_controls())
        return steps

    @property
    def controls(self) -> frozenset[str]:
        """The set of all controls used by this instruction."""
        return frozenset[str]().union(*self.steps)
