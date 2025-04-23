from flip.bytes import Byte
from flip.components.controller.instruction_memory import InstructionMemory
from flip.components.controller.instruction_memory_format import InstructionMemoryFormat
from flip.components.controller.instruction_set import InstructionSet
from flip.core import Error, Errorable


class Assembler(Errorable):
    class Error(Error): ...

    def __init__(self, instruction_set: InstructionSet) -> None:
        self.__instruction_set = instruction_set
        self.__format = InstructionMemoryFormat(instruction_set)

    def _expand_statuses(self, statuses: dict[str, bool]) -> list[dict[str, bool]]:
        def expand(statuses: dict[str, bool], status: str) -> list[dict[str, bool]]:
            if status in statuses:
                return [statuses]
            else:
                return [
                    {**statuses, status: False},
                    {**statuses, status: True},
                ]

        result = [statuses]
        for status in self.__format.statuses:
            new_result = list[dict[str, bool]]()
            for statuses in result:
                new_result.extend(expand(statuses, status))
            result = new_result
        return result

    def assemble(self) -> InstructionMemory:
        data = dict[int, int]()
        for instruction in self.__instruction_set.instructions:
            for statuses in self._expand_statuses(dict(instruction.statuses)):
                for step_index, step in enumerate(instruction.steps):
                    data[
                        self.__format.encode_address(
                            instruction.opcode,
                            statuses,
                            Byte(step_index),
                        )
                    ] = self.__format.encode_controls(step.controls)
        return InstructionMemory(data=data, format=self.__format)
