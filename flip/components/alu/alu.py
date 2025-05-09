import math
from typing import Optional, override

from flip.bytes import Byte
from flip.components.alu.operations.operation import Operation
from flip.components.alu.operations.operation_set import OperationSet
from flip.components.bus import Bus
from flip.components.component import Component
from flip.components.control import Control
from flip.components.register import Register
from flip.components.status import Status


class Alu(Component):
    def __init__(
        self,
        operation_set: OperationSet,
        bus: Bus,
        name: Optional[str] = None,
        parent: Optional[Component] = None,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.__operation_set = operation_set
        self.__num_control_bits = self._num_control_bits(self.__operation_set)
        self.__opcode_controls: list[Control] = [
            Control(name=self._opcode_control_name(i), parent=self)
            for i in range(self.__num_control_bits)
        ]
        self.__lhs = Register(name="lhs", parent=self, bus=bus)
        self.__rhs = Register(name="rhs", parent=self, bus=bus)
        self.__output = Register(name="output", parent=self, bus=bus)
        self.__rhs_one = Control(name="rhs_one", parent=self)
        self.__carry_in = Control(name="carry_in", parent=self, auto_clear=False)
        self.__carry_out = Status(name="carry_out", parent=self)
        self.__zero = Status(name="zero", parent=self)
        self.__negative = Status(name="negative", parent=self)
        self.__overflow = Status(name="overflow", parent=self)
        self.__half_carry = Status(name="half_carry", parent=self)

    @property
    def result(self) -> Byte.Result:
        return Byte.Result(
            value=self.output,
            carry=self.carry_out,
            zero=self.zero,
            negative=self.negative,
            overflow=self.overflow,
            half_carry=self.half_carry,
        )

    @result.setter
    def result(self, value: Byte.Result) -> None:
        self.output = value.value
        self.carry_out = value.carry
        self.zero = value.zero
        self.negative = value.negative
        self.overflow = value.overflow
        self.half_carry = value.half_carry

    @property
    def rhs_one(self) -> bool:
        return self.__rhs_one.value

    @rhs_one.setter
    def rhs_one(self, value: bool) -> None:
        self.__rhs_one.value = value

    @property
    def carry_out(self) -> bool:
        return self.__carry_out.value

    @carry_out.setter
    def carry_out(self, value: bool) -> None:
        self.__carry_out.value = value

    @property
    def zero(self) -> bool:
        return self.__zero.value

    @zero.setter
    def zero(self, value: bool) -> None:
        self.__zero.value = value

    @property
    def negative(self) -> bool:
        return self.__negative.value

    @negative.setter
    def negative(self, value: bool) -> None:
        self.__negative.value = value

    @property
    def overflow(self) -> bool:
        return self.__overflow.value

    @overflow.setter
    def overflow(self, value: bool) -> None:
        self.__overflow.value = value

    @property
    def half_carry(self) -> bool:
        return self.__half_carry.value

    @half_carry.setter
    def half_carry(self, value: bool) -> None:
        self.__half_carry.value = value

    @property
    def lhs(self) -> Byte:
        return self.__lhs.value

    @lhs.setter
    def lhs(self, value: Byte) -> None:
        self.__lhs.value = value

    @property
    def rhs(self) -> Byte:
        return self.__rhs.value

    @rhs.setter
    def rhs(self, value: Byte) -> None:
        self.__rhs.value = value

    @property
    def output(self) -> Byte:
        return self.__output.value

    @output.setter
    def output(self, value: Byte) -> None:
        self.__output.value = value

    @property
    def carry_in(self) -> bool:
        return self.__carry_in.value

    @carry_in.setter
    def carry_in(self, value: bool) -> None:
        self.__carry_in.value = value

    @property
    def opcode(self) -> int:
        return sum(
            (1 << i) * control.value for i, control in enumerate(self.__opcode_controls)
        )

    @opcode.setter
    def opcode(self, value: int) -> None:
        for i, control in enumerate(self.__opcode_controls):
            control.value = ((value >> i)) & 1 == 1

    @staticmethod
    def encode_opcode_controls(
        operation_set: OperationSet, operation: Operation | str | None
    ) -> frozenset[str]:
        opcode = Alu.encode_opcode(operation_set, operation)
        controls = set[str]()
        for i in range(Alu._num_control_bits(operation_set)):
            if ((opcode >> i) & 1) == 1:
                controls.add(Alu._opcode_control_name(i))
        return frozenset(controls)

    @staticmethod
    def encode_opcode(
        operation_set: OperationSet, operation: Operation | str | None
    ) -> int:
        match operation:
            case None:
                return 0
            case Operation() | str():
                return operation_set.operation_index(operation) + 1

    @staticmethod
    def decode_opcode(operation_set: OperationSet, opcode: int) -> Optional[Operation]:
        match opcode:
            case 0:
                return None
            case _:
                return operation_set.operation(opcode - 1)

    @staticmethod
    def _num_control_bits(operation_set: OperationSet) -> int:
        return math.ceil(math.log2(len(operation_set) + 1))

    @staticmethod
    def _opcode_control_name(i: int) -> str:
        return f"opcode_{i}"

    def opcode_for_operation(self, operation: Operation | str | None) -> int:
        return self.encode_opcode(self.__operation_set, operation)

    @property
    def operation_set(self) -> OperationSet:
        return self.__operation_set

    @property
    def operation(self) -> Optional[Operation]:
        if (opcode := self.opcode) == 0:
            return None
        return self.__operation_set.operations_by_index[opcode - 1]

    @override
    def _tick_read(self) -> None:
        super()._tick_read()
        if self.rhs_one:
            self.rhs = Byte(0x01)

    @override
    def _tick_process(self) -> None:
        super()._tick_process()
        if (operation := self.operation) is not None:
            result = operation(self.lhs, self.rhs, self.carry_in)
            self._log(
                f"Executing {operation.name} on {self.lhs} and {self.rhs} = {result}"
            )
            self.result = result
            self.carry_in = result.carry
