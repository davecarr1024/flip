from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Iterable, Mapping, Optional, override

from flip.bytes import Byte, Word
from flip.core import Error, Errorable
from flip.instructions import InstructionSet


@dataclass(frozen=True)
class Assembler(Errorable):
    class Error(Error): ...

    class DuplicateLabel(Error): ...

    @dataclass(frozen=True)
    class BindContext:
        labels: Mapping[str, Word]

    @dataclass(frozen=True)
    class Output(Errorable):
        class Error(Error): ...

        class DuplicatePosition(Error): ...

        memory: Mapping[Word, Byte] = field(default_factory=dict[Word, Byte])

        def _with_value(self, position: Word, value: Byte) -> "Assembler.Output":
            if position in self.memory:
                raise self._error(
                    f"{position=} already in memory.",
                    self.DuplicatePosition,
                )
            return replace(self, memory=dict(self.memory) | {position: value})

        def with_values(
            self, position: Word, values: Iterable[Byte]
        ) -> "Assembler.Output":
            for i, value in enumerate(values):
                self = self._with_value(Word(position.value + i), value)
            return self

        def with_value(self, position: Word, value: Byte | Word) -> "Assembler.Output":
            match value:
                case Byte():
                    return self._with_value(position, value)
                case Word():
                    return self.with_values(position, value.to_bytes())

    @dataclass(frozen=True)
    class Entry(Errorable, ABC):
        position: Word

        @abstractmethod
        def bind(
            self,
            context: "Assembler.BindContext",
            output: "Assembler.Output",
        ) -> "Assembler.Output":
            """Bind this entry to the given context and return the new output."""

        @abstractmethod
        def label(self) -> Optional[str]:
            """Return the label for this entry, if any."""

        @abstractmethod
        def size(self) -> int:
            """Return the size of this entry in bytes."""

    @dataclass(frozen=True)
    class Literal(Entry):
        values: tuple[Byte, ...]

        @classmethod
        def create(cls, position: Word, *values: Byte) -> "Assembler.Literal":
            return cls(position=position, values=tuple(values))

        @override
        def bind(
            self,
            context: "Assembler.BindContext",
            output: "Assembler.Output",
        ) -> "Assembler.Output":
            for i, value in enumerate(self.values):
                output = output.with_value(Word(self.position.value + i), value)
            return output

        @override
        def label(self) -> Optional[str]:
            return None

        @override
        def size(self) -> int:
            return len(self.values)

    @dataclass(frozen=True)
    class Label(Entry):
        name: str

        @override
        def bind(
            self,
            context: "Assembler.BindContext",
            output: "Assembler.Output",
        ) -> "Assembler.Output":
            return output

        @override
        def label(self) -> Optional[str]:
            return self.name

        @override
        def size(self) -> int:
            return 0

    @dataclass(frozen=True)
    class Ref(Entry):
        class Error(Error): ...

        class LabelNotFound(Error): ...

        name: str

        @override
        def bind(
            self,
            context: "Assembler.BindContext",
            output: "Assembler.Output",
        ) -> "Assembler.Output":
            if (position := context.labels.get(self.name)) is None:
                raise self._error(
                    f"Label {self.name} not found.",
                    self.LabelNotFound,
                )
            return output.with_value(self.position, position)

        @override
        def label(self) -> Optional[str]:
            return None

        @override
        def size(self) -> int:
            return 2

    instruction_set: InstructionSet
    entries: frozenset[Entry] = field(default_factory=frozenset[Entry])
    next_position: Word = field(default_factory=lambda: Word(0))

    def with_next_position(self, position: Word) -> "Assembler":
        return replace(self, next_position=position)

    def increment_next_position(self, amount: int = 1) -> "Assembler":
        return self.with_next_position(Word(self.next_position.value + amount))

    def with_entry(self, entry: Entry) -> "Assembler":
        return replace(
            self, entries=self.entries | frozenset({entry})
        ).increment_next_position(entry.size())

    def with_values(self, values: Iterable[Byte]) -> "Assembler":
        return self.with_entry(self.Literal.create(self.next_position, *values))

    def with_value(self, value: Byte | Word) -> "Assembler":
        match value:
            case Byte():
                return self.with_values([value])
            case Word():
                return self.with_values(value.to_bytes())

    def with_label(self, name: str) -> "Assembler":
        return self.with_entry(self.Label(self.next_position, name))

    def with_ref(self, name: str) -> "Assembler":
        return self.with_entry(self.Ref(self.next_position, name))

    @classmethod
    def for_program(cls, program: "program_lib.Program") -> "Assembler":
        self = cls(instruction_set=program.instruction_set)
        for statement in program.statements:
            self = statement.bind(self)
        return self

    def _labels(self) -> Mapping[str, Word]:
        labels = dict[str, Word]()
        for entry in self.entries:
            if (name := entry.label()) is not None:
                if name in labels:
                    raise self._error(
                        f"Duplicate label {name}.",
                        self.DuplicateLabel,
                    )
                labels[name] = entry.position
        return labels

    def _bind_context(self) -> "Assembler.BindContext":
        return self.BindContext(labels=self._labels())

    def assemble(self) -> "Assembler.Output":
        output = self.Output()
        context = self._bind_context()
        for entry in self.entries:
            output = entry.bind(context, output)
        return output


from flip.programs import program as program_lib
