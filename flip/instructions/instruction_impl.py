from dataclasses import dataclass, field, replace
from typing import Iterable, Iterator, Mapping, Optional, Sized, override

from flip.instructions.step import Step


@dataclass(frozen=True)
class InstructionImpl(Sized, Iterable[Step]):
    @dataclass(frozen=True)
    class _StatusEntry:
        name: str
        value: bool

    _statuses: frozenset[_StatusEntry] = field(default_factory=frozenset[_StatusEntry])
    _steps: tuple[Step, ...] = field(default_factory=tuple[Step, ...])

    @classmethod
    def create(
        cls,
        steps: Optional[Iterable[Step]] = None,
        statuses: Optional[Mapping[str, bool]] = None,
    ) -> "InstructionImpl":
        return InstructionImpl(
            _statuses=(
                frozenset(
                    InstructionImpl._StatusEntry(name=name, value=value)
                    for name, value in statuses.items()
                )
                if statuses is not None
                else frozenset()
            ),
            _steps=tuple(steps) if steps is not None else tuple(),
        )

    @property
    def statuses(self) -> Mapping[str, bool]:
        return {entry.name: entry.value for entry in self._statuses}

    def _with_steps(self, steps: Iterable[Step]) -> "InstructionImpl":
        return replace(self, _steps=tuple(steps))

    def with_steps(self, steps: Iterable[Step]) -> "InstructionImpl":
        return self._with_steps(self._steps + tuple(steps))

    def with_header(self, steps: Iterable[Step]) -> "InstructionImpl":
        return self._with_steps(tuple(steps) + self._steps)

    def with_footer(self, steps: Iterable[Step]) -> "InstructionImpl":
        return self._with_steps(self._steps + tuple(steps))

    def with_step(self, step: Step) -> "InstructionImpl":
        return self._with_steps(self._steps + (step,))

    @override
    def __len__(self) -> int:
        return len(self._steps)

    @override
    def __iter__(self) -> Iterator[Step]:
        return iter(self._steps)
