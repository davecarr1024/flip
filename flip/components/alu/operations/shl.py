from typing import override

from flip.bytes import Byte
from flip.components.alu.operations.operation import Operation


class Shl(Operation):
    @override
    def __call__(self, lhs: Byte, rhs: Byte, carry_in: bool) -> Byte.Result:
        return lhs.shift_left()
