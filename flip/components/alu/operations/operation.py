from abc import ABC, abstractmethod

from flip.bytes import Byte


class Operation(ABC):
    @property
    def name(self) -> str:
        """The name of this operation."""
        return self.__class__.__name__.lower()

    @abstractmethod
    def __call__(self, lhs: Byte, rhs: Byte, carry_in: bool) -> Byte.Result:
        """Perform the operation on the given bytes and carry_in flag."""
