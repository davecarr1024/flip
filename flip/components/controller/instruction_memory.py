from typing import Mapping, Optional

from flip.components import component


class InstructionMemory(component.Component):
    class KeyError(component.Component.KeyError, KeyError): ...

    def __init__(
        self,
        name: Optional[str] = None,
        parent: Optional[component.Component] = None,
        data: Optional[Mapping[int, int]] = None,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.__data: Mapping[int, int] = dict(data) if data is not None else {}

    def _get(self, address: int) -> int:
        try:
            return self.__data[address]
        except KeyError as e:
            raise self._error(f"Address {address} not found.", self.KeyError) from e
