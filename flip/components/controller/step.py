from dataclasses import dataclass


@dataclass(frozen=True)
class Step:
    controls: frozenset[str]

    @classmethod
    def create(cls, controls: set[str] | list[str]) -> "Step":
        return cls(controls=frozenset(controls))
