from dataclasses import dataclass, field, replace
from typing import Iterable, Iterator, Optional, Sized, override


@dataclass(frozen=True)
class Step(Sized, Iterable[str]):
    _controls: frozenset[str] = field(default_factory=frozenset[str])

    @classmethod
    def create(
        cls,
        controls: Optional[set[str] | list[str]] = None,
    ) -> "Step":
        return cls(
            _controls=frozenset(controls) if controls is not None else frozenset()
        )

    @override
    def __len__(self) -> int:
        return len(self._controls)

    @override
    def __iter__(self) -> Iterator[str]:
        return iter(self._controls)

    def _with_controls(self, controls: Iterable[str]) -> "Step":
        return replace(self, _controls=frozenset(controls))

    def with_control(self, control: str) -> "Step":
        return self._with_controls(self._controls | {control})

    def with_controls(self, controls: Iterable[str]) -> "Step":
        return self._with_controls(self._controls | frozenset(controls))
