from dataclasses import dataclass
from typing import Iterable, Iterator, Set, override


@dataclass(frozen=True)
class Step(Set[str]):
    controls: frozenset[str]

    def with_controls(self, controls: Iterable[str]) -> "Step":
        return Step(self.controls | frozenset(controls))

    def with_control(self, control: str) -> "Step":
        return self.with_controls({control})

    @override
    def __len__(self) -> int:
        return len(self.controls)

    @override
    def __iter__(self) -> Iterator[str]:
        yield from self.controls

    @override
    def __contains__(self, control: object) -> bool:
        return control in self.controls
