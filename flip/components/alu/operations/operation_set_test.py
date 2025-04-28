from dataclasses import dataclass
from typing import override

import pytest

from flip.bytes import Byte
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


def test_create() -> None:
    assert len(operation_set) == 9
    assert list(operation_set) == [adc, and_, or_, rol, ror, sbc, shl, shr, xor]
    assert list(operation_set.operations) == [
        adc,
        and_,
        or_,
        rol,
        ror,
        sbc,
        shl,
        shr,
        xor,
    ]


def test_operations_by_name() -> None:
    assert operation_set.operations_by_name == {
        "adc": adc,
        "and": and_,
        "or": or_,
        "rol": rol,
        "ror": ror,
        "sbc": sbc,
        "shl": shl,
        "shr": shr,
        "xor": xor,
    }


def test_operations_by_index() -> None:
    assert operation_set.operations_by_index == {
        0: adc,
        1: and_,
        2: or_,
        3: rol,
        4: ror,
        5: sbc,
        6: shl,
        7: shr,
        8: xor,
    }


@dataclass(frozen=True)
class _Operation(Operation):
    _name: str
    i: int

    @property
    @override
    def name(self) -> str:
        return self._name

    @override
    def __call__(self, lhs: Byte, rhs: Byte, carry_in: bool) -> Byte.Result:
        raise NotImplementedError()  # pragma: no cover


def test_duplicate_operation_name() -> None:
    with pytest.raises(OperationSet.DuplicateOperationName):
        OperationSet.create({_Operation("a", 0), _Operation("a", 2)})


def test_get_operation_name() -> None:
    assert operation_set.operation("adc") == adc


def test_get_operation_index() -> None:
    assert operation_set.operation(0) == adc


def test_get_operation_unknown_name() -> None:
    with pytest.raises(OperationSet.KeyError):
        operation_set.operation("unknown")


def test_get_operation_unknown_index() -> None:
    with pytest.raises(OperationSet.KeyError):
        operation_set.operation(20)


def test_operation_index_by_operation() -> None:
    assert operation_set.operation_index(adc) == 0


def test_operation_index_by_name() -> None:
    assert operation_set.operation_index("adc") == 0


def test_operation_index_unknown_operation() -> None:
    with pytest.raises(OperationSet.KeyError):
        operation_set.operation_index(_Operation("unknown", 0))


def test_operation_index_unknown_name() -> None:
    with pytest.raises(OperationSet.KeyError):
        operation_set.operation_index("unknown")
