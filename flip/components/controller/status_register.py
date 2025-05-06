from dataclasses import dataclass
from typing import Iterator, Mapping, Optional, override

from flip.bytes import Byte
from flip.components.bus import Bus
from flip.components.component import Component
from flip.components.control import Control
from flip.components.register import Register
from flip.core import Error, Errorable


class StatusRegister(Register):
    """A special purpose register that holds the status of the CPU.

    The format of the status register is configurable to allow for
    different cpu architectures.
    """

    @dataclass(frozen=True)
    class Format(Errorable, Mapping[str, int]):
        """Format for encoding and decoding statuses into a byte.

        This format holds a mapping of status names to bit indices in a byte.
        """

        class Error(Error): ...

        class KeyError(Error, KeyError): ...

        _status_indices: Mapping[str, int]

        def __post_init__(self) -> None:
            for status, index in self._status_indices.items():
                if not 0 <= index < 8:
                    raise self._error(
                        f"Status index {index} out of range for status {status}.",
                        self.Error,
                    )
            if len(self._status_indices) != len(set(self._status_indices.values())):
                raise self._error("Duplicate status indices found.", self.Error)

        def encode(self, statuses: Mapping[str, bool]) -> Byte:
            for status in statuses:
                if status not in self._status_indices:
                    raise self._error(
                        f"Status {status} not found.",
                        self.Error,
                    )
            return Byte(
                sum(
                    1 << index
                    for status, index in self._status_indices.items()
                    if statuses.get(status, False)
                )
            )

        def decode(self, byte: Byte) -> Mapping[str, bool]:
            return {
                status: bool(byte.unsigned_value & (1 << index))
                for status, index in self._status_indices.items()
            }

        @override
        def __len__(self) -> int:
            return len(self._status_indices)

        @override
        def __iter__(self) -> Iterator[str]:
            yield from self._status_indices

        @override
        def __getitem__(self, status: str) -> int:
            try:
                return self._status_indices[status]
            except KeyError as e:
                raise self._error(f"Status {status} not found.", self.KeyError) from e

        @classmethod
        def default(cls) -> "StatusRegister.Format":
            return cls(
                _status_indices={
                    "alu.negative": 7,
                    "alu.overflow": 6,
                    # 5: unused
                    # 4: unused or "break"
                    # 3: unused or "decimal mode"
                    # 2: maybe "interrupt_disable" (future use)
                    "alu.zero": 1,
                    "alu.carry_out": 0,
                }
            )

    def __init__(
        self,
        bus: Bus,
        name: str,
        parent: Optional[Component] = None,
        format: Optional["StatusRegister.Format"] = None,
    ) -> None:
        super().__init__(
            bus=bus,
            name=name,
            parent=parent,
        )
        self.__format = format if format is not None else self.Format.default()
        self.__latch = Control(
            name="latch",
            parent=self,
            # We manually handle clearing the latch in the clear phase.
            auto_clear=False,
        )

    @property
    def latch(self) -> bool:
        return self.__latch.value

    @latch.setter
    def latch(self, value: bool) -> None:
        self.__latch.value = value

    @property
    def status_values(self) -> Mapping[str, bool]:
        return self.__format.decode(self.value)

    @status_values.setter
    def status_values(self, statuses: Mapping[str, bool]) -> None:
        self.value = self.__format.encode(statuses)

    @override
    def _tick_clear(self) -> None:
        """Latch the status values into the register.

        Note that this happens during the clear phase, which is the last phase of
        the tick cycle. This is because the status values are typically set during
        the process phase, and we want to ensure that they are latched before the
        next tick cycle starts and Controller starts decoding the instruction.
        """
        super()._tick_clear()
        if self.latch:
            self._log(f"Latching status values: {self.root.statuses_by_path}")
            for status in self.__format:
                if status not in self.root.statuses_by_path:
                    raise self._error(
                        f"Status {status} not found in root statuses.", self.Error
                    )
            self.value = self.__format.encode(
                {
                    path: status.value
                    for path, status in self.root.statuses_by_path.items()
                    if path in self.__format
                }
            )
            self._log(f"Latched status values: {self.status_values}")
            # Manually clear the latch. Auto-clearing is disabled because we
            # want to manually handle latching at the very end of the tick cycle.
            self.latch = False
