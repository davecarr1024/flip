from typing import override

import pytest

from flip.core.validatable import Validatable


class _Validatable(Validatable):
    def __init__(self) -> None:
        super().__init__()
        self.__valid = True

    @property
    def valid(self) -> bool:
        return self.__valid

    @valid.setter
    def valid(self, value: bool) -> None:
        with self._pause_validation():
            self.__valid = value

    @override
    def _validate(self) -> None:
        if not self.valid:
            raise self._validation_error("invalid")

    def valid_operation(self) -> None:
        with self._pause_validation():
            self.valid = False
            self.valid = True

    def invalid_operation(self) -> None:
        self.valid = False


def test_valid_operation() -> None:
    v = _Validatable()
    v.valid_operation()


def test_invalid_operation() -> None:
    v = _Validatable()
    with pytest.raises(_Validatable.ValidationError) as excinfo:
        v.invalid_operation()
    assert str(excinfo.value) == "invalid"


def test_validate() -> None:
    v = _Validatable()
    v.validate()
