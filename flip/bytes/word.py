from typing import override

from flip.bytes.byte import Byte


class Word:
    def __init__(self, value: int = 0) -> None:
        self.__value = value & 0xFFFF

    @override
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Word) and self.__value == other.__value

    @override
    def __hash__(self) -> int:
        return hash(self.__value)

    @override
    def __repr__(self) -> str:
        return f"Word(0x{self.__value:04X})"

    def to_bytes(self) -> tuple[Byte, Byte]:
        return (
            Byte(self.__value & 0xFF),
            Byte((self.__value >> 8) & 0xFF),
        )

    @classmethod
    def from_bytes(cls, low: Byte, high: Byte) -> "Word":
        return cls((high.unsigned_value << 8) | low.unsigned_value)

    @property
    def value(self) -> int:
        return self.__value
