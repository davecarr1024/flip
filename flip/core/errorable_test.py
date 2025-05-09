import pytest

from flip.core.error import Error
from flip.core.errorable import Errorable


class _Errorable(Errorable):
    class ValueError(Error): ...

    def set(self, value: int) -> int:
        if value < 0:
            raise self._error("value must be non-negative", self.ValueError)
        return value

    def try_set(self, value: int) -> int:
        return self._try(lambda: self.set(value), "set failed", self.ValueError)


def test_throw() -> None:
    e = _Errorable()
    with pytest.raises(_Errorable.ValueError) as excinfo:
        e.set(-1)
    assert str(excinfo.value) == "value must be non-negative"


def test_try_success() -> None:
    e = _Errorable()
    assert e.try_set(1) == 1


def test_try_fail() -> None:
    e = _Errorable()
    with pytest.raises(_Errorable.ValueError) as excinfo:
        e.try_set(-1)
    assert str(excinfo.value) == "set failed"
