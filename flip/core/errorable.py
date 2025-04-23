from typing import Callable, Type

from flip.core.error import Error


class Errorable:
    def _error[E: Error](self, message: str, type: Type[E] = Error) -> E:
        return type(message)

    def _try[T, E: Error](
        self, f: Callable[[], T], message: str, type: Type[E] = Error
    ) -> T:
        try:
            return f()
        except Error as e:
            raise self._error(message, type) from e
