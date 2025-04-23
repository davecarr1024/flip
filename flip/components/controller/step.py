from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Step:
    controls: frozenset[str]

    @classmethod
    def create(cls, controls: Iterable[str]) -> "Step":
        return cls(controls=frozenset(controls))
