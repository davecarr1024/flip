from dataclasses import dataclass, field, replace
from typing import Iterable, Iterator, Mapping, Optional, Self, Sized, override

from flip.bytes import Byte
from flip.instructions.addressing_mode import AddressingMode


@dataclass(frozen=True)
class Instruction(Sized, Iterable["instruction_mode.InstructionMode"]):
    name: str
    _modes: frozenset["instruction_mode.InstructionMode"] = field(
        default_factory=lambda: frozenset[instruction_mode.InstructionMode]()
    )

    @classmethod
    def create(
        cls,
        name: str,
        modes: Optional[Iterable["instruction_mode.InstructionMode"]] = None,
    ) -> Self:
        return cls(
            name=name, _modes=frozenset(modes) if modes is not None else frozenset()
        )

    @dataclass(frozen=True)
    class Builder:
        instruction_set_builder: "instruction_set.InstructionSet.Builder" = field(
            repr=False, hash=False, compare=False
        )
        name: str
        _modes: frozenset["instruction_mode.InstructionMode"] = field(
            default_factory=lambda: frozenset[instruction_mode.InstructionMode]()
        )

        @property
        def opcodes(self) -> frozenset[Byte]:
            return (
                frozenset[Byte](mode.opcode for mode in self._modes)
                | self.instruction_set_builder.opcodes
            )

        def _with_modes(
            self, modes: Iterable["instruction_mode.InstructionMode"]
        ) -> "Instruction.Builder":
            return replace(self, _modes=frozenset(modes))

        def with_mode(
            self, mode: "instruction_mode.InstructionMode"
        ) -> "Instruction.Builder":
            return self._with_modes(self._modes | {mode})

        def mode(
            self, mode: AddressingMode | str
        ) -> "instruction_mode.InstructionMode.Builder":
            return instruction_mode.InstructionMode.Builder(
                instruction_builder=self,
                _mode=mode,
            )

        def end_instruction(self) -> "instruction_set.InstructionSet.Builder":
            return self.instruction_set_builder.with_instruction(
                Instruction.create(name=self.name, modes=self._modes)
            )

        def instruction(self, name: str) -> "Instruction.Builder":
            return self.end_instruction().instruction(name)

        def build(self) -> "instruction_set.InstructionSet":
            return self.end_instruction().build()

        def header(self) -> "header_builder.HeaderBuilder":
            return self.end_instruction().header()

    @classmethod
    def create_simple(
        cls,
        name: str,
        mode: AddressingMode,
        opcode: Byte,
        steps: list["step.Step"],
    ) -> Self:
        return cls(name=name).with_mode(
            instruction_mode.InstructionMode.create(mode=mode, opcode=opcode).with_impl(
                instruction_impl.InstructionImpl.create(steps=steps)
            )
        )

    @override
    def __len__(self) -> int:
        return len(self._modes)

    @override
    def __iter__(self) -> Iterator["instruction_mode.InstructionMode"]:
        return iter(self._modes)

    def _with_modes(self, modes: Iterable["instruction_mode.InstructionMode"]) -> Self:
        return replace(self, _modes=frozenset(modes))

    def with_modes(self, modes: Iterable["instruction_mode.InstructionMode"]) -> Self:
        return self._with_modes(self._modes | frozenset(modes))

    def with_mode(self, mode: "instruction_mode.InstructionMode") -> Self:
        return self._with_modes(self._modes | {mode})

    def with_header(self, steps: Iterable["step.Step"]) -> Self:
        return self._with_modes(mode.with_header(steps) for mode in self._modes)

    def with_footer(self, steps: Iterable["step.Step"]) -> Self:
        return self._with_modes(mode.with_footer(steps) for mode in self._modes)

    @property
    def controls(self) -> frozenset[str]:
        """The set of all controls used by any mode of this instruction."""
        return frozenset[str]().union(*[mode.controls for mode in self])

    @property
    def statuses(self) -> frozenset[str]:
        """The set of all statuses used by any mode of this instruction."""
        return frozenset[str]().union(*[mode.statuses for mode in self])

    @property
    def max_num_steps(self) -> int:
        return max(mode.max_num_steps for mode in self)

    @property
    def modes_by_addressing_mode(
        self,
    ) -> Mapping[AddressingMode, "instruction_mode.InstructionMode"]:
        return {mode.mode: mode for mode in self._modes}

    @property
    def opcodes(self) -> frozenset[Byte]:
        return frozenset[Byte](mode.opcode for mode in self._modes)


from flip.instructions import (
    header_builder,
    instruction_impl,
    instruction_mode,
    instruction_set,
    step,
)
