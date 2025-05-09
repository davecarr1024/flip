from pytest_subtests import SubTests

from flip.bytes import Byte
from flip.components.alu import Alu
from flip.components.alu.operations import (
    Adc,
    And,
    Operation,
    OperationSet,
    Or,
    Rol,
    Ror,
    Sbc,
    Shl,
    Shr,
    Xor,
)
from flip.components.bus import Bus
from flip.components.component import Component

adc = Adc()
and_ = And()
or_ = Or()
rol = Rol()
ror = Ror()
sbc = Sbc()
shl = Shl()
shr = Shr()
xor = Xor()


operation_set = OperationSet.create(
    {
        adc,
        and_,
        or_,
        rol,
        ror,
        sbc,
        shl,
        xor,
        shr,
    }
)

root = Component()
bus = Bus(parent=root)
alu = Alu(
    operation_set=operation_set,
    parent=root,
    bus=bus,
    name="alu",
)


def test_get_operation_set() -> None:
    assert alu.operation_set is operation_set


def test_inactive() -> None:
    """Test that the ALU does not change the output when inactive."""
    alu.output = Byte(0xAB)
    alu.opcode = 0
    alu.tick()
    assert alu.output == Byte(0xAB)


def test_encode_opcode(subtests: SubTests) -> None:
    for operation, expected in list[tuple[Operation | str | None, int]](
        [
            (None, 0),
            (adc, 1),
            ("sbc", 6),
        ]
    ):
        with subtests.test(operation=operation, expected=expected):
            assert Alu.encode_opcode(operation_set, operation) == expected


def test_decode_opcode(subtests: SubTests) -> None:
    for opcode, expected in list[tuple[int, Operation | None]](
        [
            (0, None),
            (1, adc),
            (6, sbc),
        ]
    ):
        with subtests.test(opcode=opcode, expected=expected):
            assert Alu.decode_opcode(operation_set, opcode) == expected


def test_get_opcode_for_operation(subtests: SubTests) -> None:
    for operation, expected in list[tuple[Operation | str | None, int]](
        [
            (None, 0),
            (adc, 1),
            ("sbc", 6),
        ]
    ):
        with subtests.test(operation=operation, expected=expected):
            assert alu.opcode_for_operation(operation) == expected


def test_run_operator(subtests: SubTests) -> None:
    for operation, lhs, rhs, carry_in, expected in list[
        tuple[Operation | str, Byte, Byte, bool, Byte.Result]
    ](
        [
            (
                adc,
                Byte(0x01),
                Byte(0x02),
                False,
                Byte.Result(
                    value=Byte(0x03),
                ),
            ),
        ]
    ):
        with subtests.test(
            operation=operation,
            lhs=lhs,
            rhs=rhs,
            carry_in=carry_in,
            expected=expected,
        ):
            alu.opcode = alu.opcode_for_operation(operation)
            alu.lhs = lhs
            alu.rhs = rhs
            alu.carry_in = carry_in
            alu.tick()
            assert alu.result == expected


def test_encode_opcode_controls(subtests: SubTests) -> None:
    for operation, expected in list[tuple[Operation | str | None, set[str]]](
        [
            (None, set()),
            (adc, {"opcode_0"}),
            ("sbc", {"opcode_1", "opcode_2"}),
        ]
    ):
        with subtests.test(operation=operation, expected=expected):
            assert alu.encode_opcode_controls(operation_set, operation) == expected


def test_rhs_one() -> None:
    alu.rhs = Byte(0x00)
    alu.rhs_one = False
    assert alu.rhs == Byte(0x00)
    assert not alu.rhs_one
    alu.tick()
    assert alu.rhs == Byte(0x00)
    assert not alu.rhs_one
    alu.rhs_one = True
    alu.tick()
    assert alu.rhs == Byte(0x01)
    assert not alu.rhs_one
