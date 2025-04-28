from typing import override

from flip.bytes import Byte
from flip.components.alu.operations.operation import Operation


class Rol(Operation):
    @override
    def __call__(self, lhs: Byte, rhs: Byte, carry_in: bool) -> Byte.Result:
        return lhs.roll_left(carry_in)
