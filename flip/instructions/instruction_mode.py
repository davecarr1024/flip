from dataclasses import dataclass, field, replace
from typing import Iterable, Iterator, Optional, Self, Sized, Union, overload, override

from flip.bytes import Byte
from flip.core import Error, Errorable
from flip.instructions.addressing_mode import AddressingMode


@dataclass(frozen=True)
class InstructionMode(Errorable, Sized, Iterable["instruction_impl.InstructionImpl"]):
    class Error(Error): ...

    class ValueError(Error, ValueError): ...

    @dataclass(frozen=True)
    class Builder:
        instruction_builder: "instruction.Instruction.Builder" = field(
            repr=False, hash=False, compare=False
        )
        _mode: AddressingMode | str
        _impls: frozenset["instruction_impl.InstructionImpl"] = field(
            default_factory=lambda: frozenset[instruction_impl.InstructionImpl]()
        )

        @property
        def opcodes(self) -> frozenset[Byte]:
            return self.instruction_builder.opcodes

        def next_opcode(self) -> Byte:
            return Byte(len(self.opcodes))

        def _with_impls(
            self, impls: Iterable["instruction_impl.InstructionImpl"]
        ) -> Self:
            return replace(self, _impls=frozenset(impls))

        def with_impl(self, impl: "instruction_impl.InstructionImpl") -> Self:
            return self._with_impls(self._impls | {impl})

        def impl(self, **statuses: bool) -> "instruction_impl.InstructionImpl.Builder":
            return instruction_impl.InstructionImpl.Builder.create(
                instruction_mode_builder=self,
                statuses=statuses,
            )

        @overload
        def step(
            self, control: str, *controls: str
        ) -> "instruction_impl.InstructionImpl.Builder": ...

        @overload
        def step(self) -> "step.Step.Builder": ...

        def step(
            self,
            control: Optional[str] = None,
            *controls: str,
        ) -> Union[
            "step.Step.Builder",
            "instruction_impl.InstructionImpl.Builder",
        ]:
            return self.impl().step(*[control, *controls])

        def end_mode(self) -> "instruction.Instruction.Builder":
            match self._mode:
                case AddressingMode():
                    mode = self._mode
                case str():
                    mode = AddressingMode[self._mode.upper()]
            return self.instruction_builder.with_mode(
                InstructionMode.create(
                    mode=mode,
                    impls=self._impls,
                    opcode=self.next_opcode(),
                )
            )

        def mode(self, mode: AddressingMode | str) -> "InstructionMode.Builder":
            return self.end_mode().mode(mode)

        def end_instruction(self) -> "instruction_set.InstructionSet.Builder":
            return self.end_mode().end_instruction()

        def instruction(self, name: str) -> "instruction.Instruction.Builder":
            return self.end_instruction().instruction(name)

        def build(self) -> "instruction_set.InstructionSet":
            return self.end_instruction().build()

        def header(self) -> "header_builder.HeaderBuilder":
            return self.end_instruction().header()

    mode: AddressingMode
    opcode: Byte
    _impls: frozenset["instruction_impl.InstructionImpl"]

    @override
    def __len__(self) -> int:
        return len(self._impls)

    @override
    def __iter__(self) -> Iterator["instruction_impl.InstructionImpl"]:
        return iter(self._impls)

    @classmethod
    def create(
        cls,
        mode: AddressingMode,
        opcode: Byte,
        impls: Optional[Iterable["instruction_impl.InstructionImpl"]] = None,
    ) -> Self:
        return cls(
            mode=mode,
            opcode=opcode,
            _impls=(frozenset(impls) if impls is not None else frozenset()),
        )

    def _with_impls(self, impls: Iterable["instruction_impl.InstructionImpl"]) -> Self:
        return replace(self, _impls=frozenset(impls))

    def with_impls(self, impls: Iterable["instruction_impl.InstructionImpl"]) -> Self:
        return self._with_impls(self._impls | frozenset(impls))

    def with_impl(self, impl: "instruction_impl.InstructionImpl") -> Self:
        return self._with_impls(self._impls | {impl})

    def with_header(self, steps: Iterable["step.Step"]) -> Self:
        return self._with_impls(impl.with_header(steps) for impl in self._impls)

    def with_footer(self, steps: Iterable["step.Step"]) -> Self:
        return self._with_impls(impl.with_footer(steps) for impl in self._impls)

    def with_last_step_controls(self, controls: frozenset[str]) -> Self:
        return self._with_impls(impl.with_last_step_controls(controls) for impl in self)

    @property
    def controls(self) -> frozenset[str]:
        """The set of all controls used by any impl of this mode."""
        return frozenset[str]().union(*[impl.controls for impl in self])

    @property
    def statuses(self) -> frozenset[str]:
        """The set of all statuses used by any impl of this mode."""
        return frozenset[str]().union(*[impl.statuses.keys() for impl in self])

    @property
    def max_num_steps(self) -> int:
        if not self._impls:
            raise self._error(
                f"No implementations defined for mode {self}",
                self.ValueError,
            )
        return max(map(len, self))


from flip.instructions import (
    header_builder,
    instruction,
    instruction_impl,
    instruction_set,
    step,
)
