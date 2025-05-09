import pytest
from pytest_subtests import SubTests

from flip.bytes import Byte
from flip.components.controller import (
    InstructionMemory,
)

from .instruction_memory_format_test import imf


def test_get(subtests: SubTests) -> None:
    im = InstructionMemory(
        format=imf,
        data={
            0b0_010_0: 0b00011,
            0b0_110_0: 0b00011,
            0b0_010_1: 0b00110,
            0b1_010_0: 0b01100,
        },
    )
    for opcode, statuses, step_index, controls in list[
        tuple[Byte, dict[str, bool], Byte, set[str]],
    ](
        [
            (
                Byte(0),
                {
                    "s2": True,
                },
                Byte(0),
                {"c1", "c2"},
            ),
            (
                Byte(0),
                {
                    "s2": True,
                    "s3": True,
                },
                Byte(0),
                {"c1", "c2"},
            ),
            (
                Byte(0),
                {
                    "s2": True,
                },
                Byte(1),
                {"c2", "c3"},
            ),
            (
                Byte(1),
                {
                    "s2": True,
                },
                Byte(0),
                {"c3", "c4"},
            ),
        ]
    ):
        with subtests.test(
            opcode=opcode,
            statuses=statuses,
            step_index=step_index,
            controls=controls,
        ):
            assert (
                im.get(opcode=opcode, statuses=statuses, step_index=step_index)
                == controls
            )


def test_not_found() -> None:
    im = InstructionMemory(format=imf, data={})
    with pytest.raises(InstructionMemory.KeyError):
        im.get(Byte(0), {}, Byte(0))
