from typing import Mapping, Optional

from flip.bytes import Byte
from flip.components import component
from flip.components.controller.instruction_memory_format import InstructionMemoryFormat


class InstructionMemory(component.Component):
    class KeyError(component.Component.KeyError, KeyError): ...

    def __init__(
        self,
        format: InstructionMemoryFormat,
        data: Mapping[int, int],
        name: Optional[str] = None,
        parent: Optional[component.Component] = None,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.__format = format
        self.__data = data

    @property
    def format(self) -> InstructionMemoryFormat:
        return self.__format

    def _get(self, address: int) -> int:
        try:
            return self.__data[address]
        except KeyError as e:
            raise self._error(
                f"Address {address} {address:X} {address:b} not found.", self.KeyError
            ) from e

    def get(
        self,
        opcode: Byte,
        statuses: Mapping[str, bool],
        step_index: Byte,
    ) -> frozenset[str]:
        try:
            return self.__format.decode_controls(
                self._get(
                    self.__format.encode_address(
                        opcode,
                        statuses,
                        step_index,
                    ),
                ),
            )
        except self.KeyError as e:
            raise self._error(
                f"Unable to get controls for {opcode=}, {statuses=}, {step_index=}.",
                self.KeyError,
            ) from e
