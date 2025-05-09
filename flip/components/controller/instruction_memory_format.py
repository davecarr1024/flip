import math
from typing import Iterable, Mapping

from flip.bytes import Byte
from flip.components.controller.control_mapping import ControlMapping
from flip.components.controller.status_mapping import StatusMapping
from flip.instructions import InstructionSet


class InstructionMemoryFormat:
    def __init__(self, instruction_set: InstructionSet) -> None:
        self.__controls = ControlMapping(instruction_set)
        self.__statuses = StatusMapping(instruction_set)
        self.__num_status_bits = len(self.__statuses)
        self.__num_step_index_bits = math.ceil(math.log2(instruction_set.max_num_steps))
        self.__num_opcode_bits = 8

    def encode_address(
        self,
        opcode: Byte,
        statuses: Mapping[str, bool],
        step_index: Byte,
    ) -> int:
        return (
            opcode.unsigned_value
            << (self.__num_status_bits + self.__num_step_index_bits)
            | self.__statuses.encode_address(statuses) << self.__num_step_index_bits
            | step_index.unsigned_value
        )

    def decode_address(self, address: int) -> tuple[Byte, Mapping[str, bool], Byte]:
        opcode = Byte(address >> (self.__num_status_bits + self.__num_step_index_bits))
        statuses = self.__statuses.decode_address(address >> self.__num_step_index_bits)
        step_index = Byte(address & ((1 << self.__num_step_index_bits) - 1))
        return opcode, statuses, step_index

    def encode_controls(self, controls: Iterable[str]) -> int:
        return self.__controls.encode_value(controls)

    def decode_controls(self, controls: int) -> frozenset[str]:
        return self.__controls.decode_value(controls)

    @property
    def address_size(self) -> int:
        return (
            self.__num_opcode_bits + self.__num_status_bits + self.__num_step_index_bits
        )

    @property
    def control_size(self) -> int:
        return len(self.__controls)

    @property
    def statuses(self) -> StatusMapping:
        return self.__statuses

    @property
    def controls(self) -> ControlMapping:
        return self.__controls
