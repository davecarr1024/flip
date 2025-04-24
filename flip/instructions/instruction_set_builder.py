from dataclasses import dataclass, field
from typing import Literal, Optional

from flip.bytes import Byte
from flip.core import Error, Errorable
from flip.instructions.addressing_mode import AddressingMode
from flip.instructions.instruction import Instruction
from flip.instructions.instruction_impl import InstructionImpl
from flip.instructions.instruction_mode import InstructionMode
from flip.instructions.step import Step


@dataclass(frozen=True)
class InstructionSetBuilder(Errorable):
    class Error(Error): ...

    class ValueError(Error, ValueError): ...

    _instruction_set: "instruction_set.InstructionSet" = field(
        default_factory=lambda: instruction_set.InstructionSet()
    )
    _instruction: Optional[Instruction] = None
    _mode: Optional[InstructionMode] = None
    _impl: Optional[InstructionImpl] = None

    def __post_init__(self) -> None:
        if self._mode is None:
            assert self._impl is None
        if self._instruction is None:
            assert self._mode is None

    def _collapse_impl(self) -> "InstructionSetBuilder":
        if self._impl is None:
            return self
        if self._mode is None:
            # No cover: this is an invariant violation, not a runtime error.
            raise self._error(
                "No mode to collapse impl to.", self.ValueError
            )  # pragma: no cover
        return InstructionSetBuilder(
            _instruction_set=self._instruction_set,
            _instruction=self._instruction,
            _mode=self._mode.with_impl(self._impl),
            _impl=None,
        )

    def _collapse_mode(self) -> "InstructionSetBuilder":
        if self._mode is None:
            return self
        is_ = self._collapse_impl()
        if is_._instruction is None:
            # No cover: this is an invariant violation, not a runtime error.
            raise self._error(
                "No instruction to collapse mode to.", self.ValueError
            )  # pragma: no cover
        mode = is_._mode
        if mode is None:
            # No cover: this is an invariant violation, not a runtime error.
            raise self._error(
                "No mode to collapse.", self.ValueError
            )  # pragma: no cover
        return InstructionSetBuilder(
            _instruction_set=is_._instruction_set,
            _instruction=is_._instruction.with_mode(mode),
            _mode=None,
            _impl=None,
        )

    def _collapse_instruction(self) -> "InstructionSetBuilder":
        if self._instruction is None:
            return self
        is_ = self._collapse_mode()
        instruction = is_._instruction
        if instruction is None:
            # No cover: this is an invariant violation, not a runtime error.
            raise self._error(
                "No instruction to collapse.", self.ValueError
            )  # pragma: no cover
        return InstructionSetBuilder(
            _instruction_set=is_._instruction_set.with_instruction(instruction),
            _instruction=None,
            _mode=None,
            _impl=None,
        )

    def instruction(
        self,
        name: str,
        opcode: Byte | int | None = None,
    ) -> "InstructionSetBuilder":
        is_ = self._collapse_instruction()
        is_ = InstructionSetBuilder(
            _instruction_set=is_._instruction_set,
            _instruction=Instruction.create(name=name),
            _mode=None,
            _impl=None,
        )
        match opcode:
            case int() | Byte():
                is_ = is_.mode("none", opcode)
            case None:
                pass
        return is_

    def mode(
        self,
        mode: (
            AddressingMode
            | Literal[
                "none",
                "immediate",
                "relative",
                "zero_page",
                "absolute",
            ]
        ),
        opcode: Byte | int,
    ) -> "InstructionSetBuilder":
        match mode:
            case "none":
                mode = AddressingMode.NONE
            case "immediate":
                mode = AddressingMode.IMMEDIATE
            case "relative":
                mode = AddressingMode.RELATIVE
            case "zero_page":
                mode = AddressingMode.ZERO_PAGE
            case "absolute":
                mode = AddressingMode.ABSOLUTE
            case AddressingMode():
                pass

        match opcode:
            case int():
                opcode = Byte(opcode)
            case Byte():
                pass

        is_ = self._collapse_mode()
        if is_._instruction is None:
            raise self._error("No instruction to add mode to.", self.ValueError)
        return InstructionSetBuilder(
            _instruction_set=is_._instruction_set,
            _instruction=is_._instruction,
            _mode=InstructionMode.create(mode=mode, opcode=opcode),
            _impl=None,
        )

    def impl(self, **statuses: bool) -> "InstructionSetBuilder":
        is_ = self._collapse_impl()
        if is_._mode is None:
            raise self._error("No mode to add impl to.", self.ValueError)
        return InstructionSetBuilder(
            _instruction_set=is_._instruction_set,
            _instruction=is_._instruction,
            _mode=is_._mode,
            _impl=InstructionImpl.create(statuses=statuses),
        )

    def step(self, *controls: str) -> "InstructionSetBuilder":
        if self._impl is None:
            try:
                return self.impl().step(*controls)
            except self.Error as e:
                raise self._error(
                    "Unable to create default impl to add step to.", self.ValueError
                ) from e
        return InstructionSetBuilder(
            _instruction_set=self._instruction_set,
            _instruction=self._instruction,
            _mode=self._mode,
            _impl=self._impl.with_step(Step.create(controls=list(controls))),
        )

    def build(self) -> "instruction_set.InstructionSet":
        return self._collapse_instruction()._instruction_set


from flip.instructions import instruction_set
