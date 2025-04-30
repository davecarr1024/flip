from dataclasses import dataclass, field, replace
from typing import Iterable, Optional, Self, Union, overload


@dataclass(frozen=True)
class HeaderBuilder:
    @dataclass(frozen=True)
    class StepBuilder:
        header_builder: "HeaderBuilder" = field(
            repr=False,
            hash=False,
            compare=False,
            kw_only=True,
        )
        _controls: frozenset[str] = field(default_factory=frozenset[str])

        def _with_controls(self, controls: Iterable[str]) -> Self:
            return replace(self, _controls=frozenset(controls))

        def with_controls(self, controls: Iterable[str]) -> Self:
            return self._with_controls(self._controls | frozenset(controls))

        def control(self, *controls: str) -> Self:
            return self.with_controls(controls)

        def end_step(self) -> "HeaderBuilder":
            return self.header_builder.with_step(
                step.Step.create(controls=self._controls)
            )

        @overload
        def step(self) -> "HeaderBuilder.StepBuilder": ...

        @overload
        def step(self, control: str, *controls: str) -> "HeaderBuilder": ...

        def step(
            self,
            control: Optional[str] = None,
            *controls: str,
        ) -> Union[
            "HeaderBuilder.StepBuilder",
            "HeaderBuilder",
        ]:
            match control:
                case None:
                    return self.end_step().step()
                case _:
                    return self.end_step().step(*[control, *controls])

        def header(self) -> "HeaderBuilder":
            return self.end_step().header()

        def build(self) -> "instruction_set.InstructionSet":
            return self.end_step().build()

    instruction_set: "instruction_set.InstructionSet" = field(kw_only=True)
    steps: tuple["step.Step", ...] = field(
        default_factory=lambda: tuple[step.Step, ...]()
    )

    def _with_steps(
        self,
        steps: Iterable["step.Step"],
    ) -> Self:
        return replace(self, steps=tuple(steps))

    def with_step(
        self,
        step: "step.Step",
    ) -> Self:
        return self._with_steps(self.steps + (step,))

    @overload
    def step(self) -> "StepBuilder": ...

    @overload
    def step(self, control: str, *controls: str) -> Self: ...

    def step(self, control: Optional[str] = None, *controls: str) -> Union[
        "StepBuilder",
        Self,
    ]:
        match control:
            case None:
                return self.StepBuilder(header_builder=self)
            case _:
                return self.with_step(step.Step.create(controls=[control, *controls]))

    def header(self) -> Self:
        return self

    def build(self) -> "instruction_set.InstructionSet":
        return self.instruction_set.with_header(*self.steps)


from flip.instructions import instruction_set, step
