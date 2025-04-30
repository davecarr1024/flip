from dataclasses import dataclass, field, replace
from typing import (
    Iterable,
    Iterator,
    Mapping,
    Optional,
    Self,
    Sized,
    Union,
    overload,
    override,
)

from flip.instructions.addressing_mode import AddressingMode


@dataclass(frozen=True)
class InstructionImpl(Sized, Iterable["step.Step"]):
    """A single implementation of an instruction mode.

    An implementation is a sequence of steps, each of which is a set of controls.
    An implementation may also have a set of statuses, which are boolean values
    that come from cpu status flags. These are used to determine which implementation
    to use for a given instruction mode.
    """

    @dataclass(frozen=True)
    class _StatusEntry:
        """A single hashable status=value entry."""

        name: str
        value: bool

    @dataclass(frozen=True)
    class _StatusEntrySet:
        """A hashable set of status=value entries."""

        _statuses: frozenset["InstructionImpl._StatusEntry"] = field(
            default_factory=lambda: frozenset[InstructionImpl._StatusEntry]()
        )

        @classmethod
        def encode(cls, statuses: Optional[Mapping[str, bool]]) -> Self:
            return (
                cls(
                    _statuses=frozenset[InstructionImpl._StatusEntry](
                        InstructionImpl._StatusEntry(name=name, value=value)
                        for name, value in statuses.items()
                    )
                )
                if statuses is not None
                else cls(_statuses=frozenset[InstructionImpl._StatusEntry]())
            )

        def decode(self) -> Mapping[str, bool]:
            return {entry.name: entry.value for entry in self._statuses}

    @dataclass(frozen=True)
    class Builder:
        instruction_mode_builder: "instruction_mode.InstructionMode.Builder" = field(
            repr=False, hash=False, compare=False
        )
        _statuses: "InstructionImpl._StatusEntrySet" = field(
            default_factory=lambda: InstructionImpl._StatusEntrySet()
        )
        _steps: tuple["step.Step", ...] = field(
            default_factory=lambda: tuple[step.Step, ...]()
        )

        @classmethod
        def create(
            cls,
            instruction_mode_builder: "instruction_mode.InstructionMode.Builder",
            statuses: Optional[Mapping[str, bool]] = None,
        ) -> Self:
            return cls(
                instruction_mode_builder=instruction_mode_builder,
                _statuses=InstructionImpl._StatusEntrySet.encode(statuses),
            )

        @property
        def statuses(self) -> Mapping[str, bool]:
            return self._statuses.decode()

        def _with_steps(self, steps: Iterable["step.Step"]) -> Self:
            return replace(self, _steps=tuple(steps))

        def with_step(self, step_: "step.Step") -> Self:
            return self._with_steps(self._steps + (step_,))

        @overload
        def step(self, control: str, *controls: str) -> Self: ...

        @overload
        def step(self) -> "step.Step.Builder": ...

        def step(
            self,
            control: Optional[str] = None,
            *controls: str,
        ) -> Union["step.Step.Builder", Self]:
            match control:
                case None:
                    return step.Step.Builder(instruction_impl_builder=self)
                case _:
                    return self.with_step(
                        step.Step.create(controls=[control, *controls])
                    )

        def end_impl(self) -> "instruction_mode.InstructionMode.Builder":
            return self.instruction_mode_builder.with_impl(
                InstructionImpl.create(
                    statuses=self.statuses,
                    steps=self._steps,
                )
            )

        def impl(self, **statuses: bool) -> "InstructionImpl.Builder":
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

    _statuses: _StatusEntrySet = field(
        default_factory=lambda: InstructionImpl._StatusEntrySet()
    )
    _steps: tuple["step.Step", ...] = field(default_factory=tuple["step.Step", ...])

    @classmethod
    def create(
        cls,
        steps: Optional[
            Union[
                list["step.Step"],
                tuple["step.Step", ...],
            ]
        ] = None,
        statuses: Optional[Mapping[str, bool]] = None,
    ) -> "InstructionImpl":
        return InstructionImpl(
            _statuses=cls._StatusEntrySet.encode(statuses),
            _steps=tuple(steps) if steps is not None else tuple(),
        )

    @property
    def statuses(self) -> Mapping[str, bool]:
        return self._statuses.decode()

    def _with_steps(self, steps: Iterable["step.Step"]) -> "InstructionImpl":
        return replace(self, _steps=tuple(steps))

    def with_steps(self, steps: Iterable["step.Step"]) -> "InstructionImpl":
        return self._with_steps(self._steps + tuple(steps))

    def with_header(self, steps: Iterable["step.Step"]) -> "InstructionImpl":
        return self._with_steps(tuple(steps) + self._steps)

    def with_footer(self, steps: Iterable["step.Step"]) -> "InstructionImpl":
        return self._with_steps(self._steps + tuple(steps))

    def with_step(self, step: "step.Step") -> "InstructionImpl":
        return self._with_steps(self._steps + (step,))

    @override
    def __len__(self) -> int:
        return len(self._steps)

    @override
    def __iter__(self) -> Iterator["step.Step"]:
        return iter(self._steps)

    @property
    def controls(self) -> frozenset[str]:
        """The set of all controls in the steps of this impl."""
        return frozenset[str]().union(*self._steps)


from flip.instructions import (
    header_builder,
    instruction,
    instruction_mode,
    instruction_set,
    step,
)
