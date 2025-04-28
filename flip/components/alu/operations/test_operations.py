from pytest_subtests import SubTests

from flip.bytes import Byte
from flip.components.alu.operations import (
    Adc,
    And,
    Operation,
    Or,
    Rol,
    Ror,
    Sbc,
    Shl,
    Shr,
    Xor,
)


def test_operations(subtests: SubTests) -> None:
    for operation, lhs, rhs, carry_in, expected in list[
        tuple[Operation, Byte, Byte, bool, Byte.Result]
    ](
        [
            (
                Adc(),
                Byte(0x01),
                Byte(0x02),
                False,
                Byte.Result(
                    value=Byte(0x03),
                ),
            ),
            (
                Sbc(),
                Byte(0x03),
                Byte(0x02),
                True,
                Byte.Result(
                    value=Byte(0x01),
                    carry=True,
                ),
            ),
            (
                And(),
                Byte(0x03),
                Byte(0x02),
                False,
                Byte.Result(
                    value=Byte(0x02),
                ),
            ),
            (
                Or(),
                Byte(0x01),
                Byte(0x02),
                False,
                Byte.Result(value=Byte(0x03)),
            ),
            (
                Xor(),
                Byte(0x03),
                Byte(0x01),
                False,
                Byte.Result(value=Byte(0x02)),
            ),
            (
                Shl(),
                Byte(0x01),
                Byte(0x00),  # rhs ignored for shift ops
                False,
                Byte.Result(value=Byte(0x02)),
            ),
            (
                Shr(),
                Byte(0x02),
                Byte(0x00),  # rhs ignored
                False,
                Byte.Result(value=Byte(0x01)),
            ),
            (
                Rol(),
                Byte(0b10000000),
                Byte(0x00),
                True,
                Byte.Result(
                    value=Byte(0x01),
                    carry=True,
                ),  # roll a bit out and a bit in
            ),
            (
                Ror(),
                Byte(0b00000001),
                Byte(0x00),
                True,
                Byte.Result(
                    value=Byte(0x80),
                    carry=True,
                    negative=True,
                ),  # roll a bit out and a bit in
            ),
        ]
    ):
        with subtests.test(
            operation=operation, lhs=lhs, rhs=rhs, carry_in=carry_in, expected=expected
        ):
            assert operation(lhs, rhs, carry_in) == expected
