import pytest
from pytest_subtests import SubTests

from flip.bytes import Byte, Result


def test_ctor() -> None:
    b = Byte(0x01)
    assert b.unsigned_value == 0x01


def test_ctor_mod() -> None:
    b = Byte(0x101)
    assert b.unsigned_value == 0x01


def test_set_unsigned_value() -> None:
    b = Byte()
    assert b.unsigned_value == 0x00
    b.unsigned_value = 0x01
    assert b.unsigned_value == 0x01


def test_set_signed_value() -> None:
    b = Byte()
    assert b.signed_value == 0x00
    b.signed_value = 0x01
    assert b.signed_value == 0x01
    b.signed_value = -0x01
    assert b.signed_value == -0x01


def test_len() -> None:
    b = Byte()
    assert len(b) == 8


def test_bit() -> None:
    b = Byte(0x01)
    assert b[0]
    assert not b[1]
    with pytest.raises(Byte.IndexError):
        b[8]


def test_iter() -> None:
    assert list(Byte(0x81)) == [True, False, False, False, False, False, False, True]


def test_eq() -> None:
    b = Byte(0x01)
    assert b == Byte(0x01)
    assert b != Byte(0x02)
    assert hash(b) == hash(Byte(0x01))
    assert hash(b) != hash(Byte(0x02))


def test_add(subtests: SubTests) -> None:
    for lhs, rhs, carry_in, expected in list[tuple[Byte, Byte, bool, Result]](
        [
            (
                Byte(0),
                Byte(0),
                False,
                Result(
                    value=Byte(0),
                    zero=True,
                ),
            ),
            (
                Byte(1),
                Byte(0),
                False,
                Result(
                    value=Byte(1),
                ),
            ),
            (
                Byte(0),
                Byte(1),
                False,
                Result(
                    value=Byte(1),
                ),
            ),
            (
                Byte(0),
                Byte(0),
                True,
                Result(
                    value=Byte(1),
                ),
            ),
            (
                Byte(0x0F),
                Byte(0x01),
                False,
                Result(
                    value=Byte(0x10),
                    half_carry=True,
                ),
            ),
            (
                Byte(0xFF),
                Byte(1),
                False,
                Result(
                    value=Byte(0),
                    carry=True,
                    half_carry=True,
                    zero=True,
                ),
            ),
            (
                Byte(0x01),
                Byte(-0x02),
                False,
                Result(
                    value=Byte(-0x01),
                    negative=True,
                ),
            ),
            (
                Byte(0x80),  # -128
                Byte(0x80),  # -128 → -256 → wraps to 0
                False,
                Result(
                    value=Byte(0x00),
                    overflow=True,
                    zero=True,
                    carry=True,
                ),
            ),
            (
                Byte(0x7F),
                Byte(0x01),
                False,
                Result(
                    value=Byte(0x80),
                    overflow=True,
                    half_carry=True,
                    negative=True,
                ),
            ),
        ]
    ):
        with subtests.test(lhs=lhs, rhs=rhs, carry_in=carry_in, expected=expected):
            assert lhs.add(rhs, carry_in) == expected


def test_sub(subtests: SubTests) -> None:
    for lhs, rhs, carry_in, expected in list[tuple[Byte, Byte, bool, Result]](
        [
            (
                Byte(0x00),
                Byte(0x00),
                True,
                Result(
                    value=Byte(0x00),
                    zero=True,
                    carry=True,
                ),
            ),
            (
                Byte(0x01),
                Byte(0x01),
                True,
                Result(
                    value=Byte(0x00),
                    zero=True,
                    carry=True,
                ),
            ),
            (
                Byte(0x01),
                Byte(0x02),
                True,
                Result(
                    value=Byte(0xFF),
                    negative=True,
                    half_carry=True,
                ),
            ),
            (
                Byte(0x80),
                Byte(0xFF),
                True,
                Result(
                    value=Byte(0x81),
                    negative=True,
                    half_carry=True,
                ),
            ),
            (
                Byte(0x7F),
                Byte(0xFF),
                True,
                Result(
                    value=Byte(0x80),
                    overflow=True,
                    negative=True,
                ),
            ),
            (
                Byte(0x10),
                Byte(0x01),
                True,
                Result(
                    value=Byte(0x0F),
                    carry=True,
                    half_carry=True,
                ),
            ),
            (
                Byte(0x10),
                Byte(0x11),
                True,
                Result(
                    value=Byte(0xFF),
                    negative=True,
                    half_carry=True,
                ),
            ),
        ]
    ):
        with subtests.test(lhs=lhs, rhs=rhs, carry_in=carry_in, expected=expected):
            assert lhs.sub(rhs, carry_in) == expected


def test_and(subtests: SubTests) -> None:
    for lhs, rhs, expected in list[tuple[Byte, Byte, Result]](
        [
            (
                Byte(0x01),
                Byte(0x03),
                Result(
                    value=Byte(0x01),
                ),
            ),
            (
                Byte(0x01),
                Byte(0x02),
                Result(
                    value=Byte(0x00),
                    zero=True,
                ),
            ),
            (
                Byte(0xF0),
                Byte(0xF1),
                Result(
                    value=Byte(0xF0),
                    negative=True,
                ),
            ),
        ]
    ):
        with subtests.test(lhs=lhs, rhs=rhs, expected=expected):
            assert lhs.and_(rhs) == expected


def test_or(subtests: SubTests) -> None:
    for lhs, rhs, expected in list[tuple[Byte, Byte, Result]](
        [
            (
                Byte(0x01),
                Byte(0x02),
                Result(
                    value=Byte(0x03),
                ),
            ),
            (
                Byte(0x00),
                Byte(0x00),
                Result(
                    value=Byte(0x00),
                    zero=True,
                ),
            ),
            (
                Byte(0xF0),
                Byte(0xF1),
                Result(
                    value=Byte(0xF1),
                    negative=True,
                ),
            ),
        ]
    ):
        with subtests.test(lhs=lhs, rhs=rhs, expected=expected):
            assert lhs.or_(rhs) == expected


def test_xor(subtests: SubTests) -> None:
    for lhs, rhs, expected in list[tuple[Byte, Byte, Result]](
        [
            (
                Byte(0x01),
                Byte(0x02),
                Result(
                    value=Byte(0x03),
                ),
            ),
            (
                Byte(0x01),
                Byte(0x01),
                Result(
                    value=Byte(0x00),
                    zero=True,
                ),
            ),
            (
                Byte(0xF0),
                Byte(0x01),
                Result(
                    value=Byte(0xF1),
                    negative=True,
                ),
            ),
        ]
    ):
        with subtests.test(lhs=lhs, rhs=rhs, expected=expected):
            assert lhs.xor(rhs) == expected


def test_shift_left(subtests: SubTests) -> None:
    for value, expected in list[tuple[Byte, Result]](
        [
            (
                Byte(0x01),
                Result(
                    value=Byte(0x02),
                ),
            ),
            (
                Byte(0x80),
                Result(
                    value=Byte(0x00),
                    carry=True,
                    zero=True,
                ),
            ),
            (
                Byte(0x81),
                Result(
                    value=Byte(0x02),
                    carry=True,
                ),
            ),
            (
                Byte(0x7F),
                Result(
                    value=Byte(0xFE),
                    negative=True,
                ),
            ),
        ]
    ):
        with subtests.test(value=value, expected=expected):
            assert value.shift_left() == expected


def test_shift_right(subtests: SubTests) -> None:
    for value, expected in list[tuple[Byte, Result]](
        [
            (
                Byte(0x01),
                Result(
                    value=Byte(0x00),
                    carry=True,
                    zero=True,
                ),
            ),
            (
                Byte(0x03),
                Result(
                    value=Byte(0x01),
                    carry=True,
                ),
            ),
            (
                Byte(0x80),
                Result(
                    value=Byte(0x40),
                ),
            ),
        ]
    ):
        with subtests.test(value=value, expected=expected):
            assert value.shift_right() == expected


def test_roll_left(subtests: SubTests) -> None:
    for value, carry_in, expected in list[tuple[Byte, bool, Result]](
        [
            (
                Byte(0x01),
                False,
                Result(
                    value=Byte(0x02),
                ),
            ),
            (
                Byte(0x80),
                False,
                Result(
                    value=Byte(0x00),
                    carry=True,
                    zero=True,
                ),
            ),
            (
                Byte(0x80),
                True,
                Result(
                    value=Byte(0x01),
                    carry=True,
                ),
            ),
            (
                Byte(0x7F),
                False,
                Result(
                    value=Byte(0xFE),
                    negative=True,
                ),
            ),
        ]
    ):
        with subtests.test(value=value, carry_in=carry_in, expected=expected):
            assert value.roll_left(carry_in) == expected


def test_roll_right(subtests: SubTests):
    for value, carry_in, expected in list[tuple[Byte, bool, Result]](
        [
            (
                Byte(0x01),
                False,
                Result(
                    value=Byte(0x00),
                    carry=True,
                    zero=True,
                ),
            ),
            (
                Byte(0x03),
                False,
                Result(
                    value=Byte(0x01),
                    carry=True,
                ),
            ),
            (
                Byte(0x80),
                False,
                Result(
                    value=Byte(0x40),
                ),
            ),
            (
                Byte(0x00),
                True,
                Result(
                    value=Byte(0x80),
                    negative=True,
                ),
            ),
        ]
    ):
        with subtests.test(value=value, carry_in=carry_in, expected=expected):
            assert value.roll_right(carry_in) == expected
