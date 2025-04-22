from pytest_subtests import SubTests

from flip.bytes import Byte, Word


def test_ctor_mod(subtests: SubTests) -> None:
    for value, expected in list[tuple[int, Word]](
        [
            (0x0000, Word(0x0000)),
            (0x0001, Word(0x0001)),
            (0xFFFF, Word(0xFFFF)),
            (0x10000, Word(0x0000)),
        ]
    ):
        with subtests.test(value=value, expected=expected):
            assert Word(value) == expected


def test_eq() -> None:
    w = Word(0x0001)
    assert w == Word(0x0001)
    assert w != Word(0x0002)
    assert hash(w) == hash(Word(0x0001))
    assert hash(w) != hash(Word(0x0002))


def test_to_bytes() -> None:
    assert Word(0x1234).to_bytes() == (
        Byte(0x34),
        Byte(0x12),
    )


def test_from_bytes() -> None:
    assert Word.from_bytes(Byte(0x34), Byte(0x12)) == Word(0x1234)
