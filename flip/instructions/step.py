from dataclasses import dataclass, field, replace
from typing import Iterable, Iterator, Optional, Self, Sized, Union, overload, override

from flip.instructions.addressing_mode import AddressingMode


@dataclass(frozen=True)
class Step(Sized, Iterable[str]):
    _controls: frozenset[str] = field(default_factory=frozenset[str])

    @dataclass(frozen=True)
    class Builder:
        instruction_impl_builder: "instruction_impl.InstructionImpl.Builder" = field(
            repr=False, hash=False, compare=False
        )
        _controls: frozenset[str] = field(default_factory=frozenset[str])

        def _with_controls(self, controls: Iterable[str]) -> Self:
            return replace(self, _controls=frozenset(controls))

        def with_controls(self, controls: Iterable[str]) -> Self:
            return self._with_controls(self._controls | frozenset(controls))

        def control(self, *controls: str) -> Self:
            return self.with_controls(controls)

        def end_step(self) -> "instruction_impl.InstructionImpl.Builder":
            return self.instruction_impl_builder.with_step(
                Step.create(controls=self._controls)
            )

        @overload
        def step(self) -> "Step.Builder": ...

        @overload
        def step(
            self, control: str, *controls: str
        ) -> "instruction_impl.InstructionImpl.Builder": ...

        def step(
            self,
            control: Optional[str] = None,
            *controls: str,
        ) -> Union[
            "Step.Builder",
            "instruction_impl.InstructionImpl.Builder",
        ]:
            return self.end_step().step(*[control, *controls])

        def end_impl(self) -> "instruction_mode.InstructionMode.Builder":
            return self.end_step().end_impl()

        def impl(self, **statuses: bool) -> "instruction_impl.InstructionImpl.Builder":
            return self.end_impl().impl(**statuses)

        def end_mode(self) -> "instruction.Instruction.Builder":
            return self.end_impl().end_mode()

        def mode(
            self, mode: AddressingMode | str
        ) -> "instruction_mode.InstructionMode.Builder":
            return self.end_mode().mode(mode)

        def end_instruction(self) -> "instruction_set.InstructionSet.Builder":
            return self.end_mode().end_instruction()

        def instruction(self, name: str) -> "instruction.Instruction.Builder":
            return self.end_instruction().instruction(name)

        def build(self) -> "instruction_set.InstructionSet":
            return self.end_instruction().build()

        def header(self) -> "header_builder.HeaderBuilder":
            return self.end_instruction().header()

    @classmethod
    def create(
        cls,
        controls: Optional[set[str] | frozenset[str] | list[str]] = None,
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


from flip.instructions import (
    header_builder,
    instruction,
    instruction_impl,
    instruction_mode,
    instruction_set,
)
