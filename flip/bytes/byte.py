from dataclasses import dataclass
from typing import Iterable, Iterator, Sized, override

from flip.core import Error, Errorable


class Byte(Errorable, Sized, Iterable[bool]):
    class Error(Error): ...

    class IndexError(Error, IndexError): ...

    class ValueError(Error, ValueError): ...

    @dataclass(frozen=True, kw_only=True)
    class Result:
        value: "Byte"
        carry: bool = False  # Set if result > 255 (unsigned overflow)
        zero: bool = False  # Set if result == 0
        negative: bool = False  # Set if bit 7 (MSB) is 1
        overflow: bool = False  # Set if signed overflow (see rule below)
        half_carry: bool = False  # Set if carry from bit 3 to bit 4 (BCD)

        def __repr__(self) -> str:
            flags = list[str]()
            if self.carry:
                flags.append("C")
            if self.zero:
                flags.append("Z")
            if self.negative:
                flags.append("N")
            if self.overflow:
                flags.append("V")
            if self.half_carry:
                flags.append("H")
            return f"<{self.value!r} {' '.join(flags)}>"

    def __init__(self, value: int = 0) -> None:
        self.__value = value & 0xFF

    @override
    def __repr__(self) -> str:
        return f"Byte(0x{self.unsigned_value:02X})"

    @override
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Byte) and self.__value == other.__value

    @override
    def __hash__(self) -> int:
        return hash(self.__value)

    def bit(self, index: int) -> bool:
        """Get bit at index, where 0 is LSB and 7 is MSB."""
        if not 0 <= index < 8:
            raise self._error(f"Index {index} out of range.", self.IndexError)
        return (self.__value >> index) & 1 == 1

    @property
    def bits(self) -> Iterable[bool]:
        """Iterate bits from LSB to MSB."""
        return [self.bit(i) for i in range(8)]

    def __getitem__(self, index: int) -> bool:
        return self.bit(index)

    @override
    def __iter__(self) -> Iterator[bool]:
        yield from self.bits

    @override
    def __len__(self) -> int:
        return 8

    @property
    def signed_value(self) -> int:
        return self.__value if self.__value < 128 else self.__value - 256

    @signed_value.setter
    def signed_value(self, value: int) -> None:
        self.__value = value & 0xFF

    @property
    def unsigned_value(self) -> int:
        return self.__value

    @unsigned_value.setter
    def unsigned_value(self, value: int) -> None:
        self.__value = value & 0xFF

    def add(self, rhs: "Byte", carry_in: bool = False) -> "Byte.Result":
        a = self.unsigned_value
        b = rhs.unsigned_value
        carry_int = 1 if carry_in else 0
        total = a + b + carry_int
        result_ = total & 0xFF

        return Byte.Result(
            value=Byte(result_),
            carry=total > 0xFF,
            zero=result_ == 0,
            negative=(result_ & 0x80) != 0,
            overflow=((a ^ b) & 0x80 == 0) and ((a ^ result_) & 0x80 != 0),
            half_carry=((a & 0xF) + (b & 0xF) + carry_int) > 0xF,
        )

    def sub(self, rhs: "Byte", carry_in: bool = True) -> "Byte.Result":
        a = self.unsigned_value
        b = rhs.unsigned_value
        borrow = 0 if carry_in else 1  # carry_in=True means no borrow

        total = a - b - borrow
        result_ = total & 0xFF

        return Byte.Result(
            value=Byte(result_),
            # In subtraction, carry means NO borrow happened.
            carry=(a - b - borrow) >= 0,
            zero=result_ == 0,
            negative=(result_ & 0x80) != 0,
            # Signed overflow occurs if the signs of A and B differ
            # and the sign of the result is different from A
            overflow=((a ^ b) & 0x80 != 0) and ((a ^ result_) & 0x80 != 0),
            # Half-carry (borrow from bit 4)
            half_carry=((a & 0xF) - (b & 0xF) - borrow) < 0,
        )

    def and_(self, rhs: "Byte") -> "Byte.Result":
        result_ = self.unsigned_value & rhs.unsigned_value
        return Byte.Result(
            value=Byte(result_),
            zero=result_ == 0,
            negative=(result_ & 0x80) != 0,
        )

    def or_(self, rhs: "Byte") -> "Byte.Result":
        result_ = self.unsigned_value | rhs.unsigned_value
        return Byte.Result(
            value=Byte(result_),
            zero=result_ == 0,
            negative=(result_ & 0x80) != 0,
        )

    def xor(self, rhs: "Byte") -> "Byte.Result":
        result_ = self.unsigned_value ^ rhs.unsigned_value
        return Byte.Result(
            value=Byte(result_), zero=result_ == 0, negative=(result_ & 0x80) != 0
        )

    def shift_left(self) -> "Byte.Result":
        a = self.unsigned_value
        result_ = (a << 1) & 0xFF
        return Byte.Result(
            value=Byte(result_),
            zero=result_ == 0,
            negative=(result_ & 0x80) != 0,
            carry=(a & 0x80) != 0,
        )

    def shift_right(self) -> "Byte.Result":
        a = self.unsigned_value
        result_ = (a >> 1) & 0xFF
        return Byte.Result(
            value=Byte(result_),
            zero=result_ == 0,
            negative=(result_ & 0x80) != 0,
            carry=(a & 0x01) != 0,
        )

    def roll_left(self, carry_in: bool = False) -> "Byte.Result":
        a = self.unsigned_value
        result_ = ((a << 1) | (1 if carry_in else 0)) & 0xFF
        return Byte.Result(
            value=Byte(result_),
            zero=result_ == 0,
            negative=(result_ & 0x80) != 0,
            carry=(a & 0x80) != 0,
        )

    def roll_right(self, carry_in: bool = False) -> "Byte.Result":
        a = self.unsigned_value
        result_ = ((a >> 1) | (0x80 if carry_in else 0)) & 0xFF
        return Byte.Result(
            value=Byte(result_),
            zero=result_ == 0,
            negative=(result_ & 0x80) != 0,
            carry=(a & 0x01) != 0,
        )
