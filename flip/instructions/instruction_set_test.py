from flip.bytes import Byte
from flip.instructions import (
    AddressingMode,
    Instruction,
    InstructionImpl,
    InstructionMode,
    InstructionSet,
    Step,
)

i1 = Instruction.create(
    name="i1",
    modes={
        InstructionMode.create(
            mode=AddressingMode.IMMEDIATE,
            opcode=Byte(0x01),
            impls={
                InstructionImpl.create(
                    statuses={"a": True, "b": False},
                    steps=[
                        Step.create({"c1", "c2"}),
                        Step.create({"c2", "c3"}),
                    ],
                ),
                InstructionImpl.create(
                    statuses={"c": False, "d": True},
                    steps=[
                        Step.create({"c3", "c4"}),
                        Step.create({"c3", "c4"}),
                        Step.create({"c4", "c5"}),
                    ],
                ),
            },
        ),
        InstructionMode.create(
            mode=AddressingMode.ABSOLUTE,
            opcode=Byte(0x02),
            impls={
                InstructionImpl.create(
                    statuses={"e": True, "f": True},
                    steps=[Step.create({"c5", "c6"}), Step.create({"c6", "c7"})],
                ),
            },
        ),
    },
)
i2 = Instruction.create(
    name="i2",
    modes={
        InstructionMode.create(
            mode=AddressingMode.IMMEDIATE,
            opcode=Byte(0x03),
            impls={
                InstructionImpl.create(
                    statuses={"a": True, "b": False},
                    steps=[Step.create({"c1", "c2"}), Step.create({"c2", "c3"})],
                ),
            },
        ),
    },
)
i3 = Instruction.create(
    name="i3",
    modes={
        InstructionMode.create(
            mode=AddressingMode.IMMEDIATE,
            opcode=Byte(0x04),
            impls={
                InstructionImpl.create(
                    statuses={"a": True, "b": False},
                    steps=[Step.create({"c1", "c2"}), Step.create({"c2", "c3"})],
                ),
            },
        ),
    },
)
is_ = InstructionSet.create({i1, i2})


def test_create() -> None:
    assert set(is_) == {i1, i2}
    assert len(is_) == 2


def test_create_empty() -> None:
    assert set(InstructionSet.create()) == set()


def test_ctor_empty() -> None:
    assert set(InstructionSet()) == set()


def test_with_instructions() -> None:
    assert set(is_.with_instructions({i3})) == {i1, i2, i3}


def test_with_instruction() -> None:
    assert set(is_.with_instruction(i3)) == {i1, i2, i3}


def test_with_header() -> None:
    s1 = Step().with_control("ch1")
    s2 = Step().with_control("ch2")
    assert set(is_.with_header(s1, s2)) == {i.with_header([s1, s2]) for i in {i1, i2}}


def test_with_footer() -> None:
    s1 = Step().with_control("cf1")
    s2 = Step().with_control("cf2")
    assert set(is_.with_footer(s1, s2)) == {i.with_footer([s1, s2]) for i in {i1, i2}}


def test_controls() -> None:
    assert is_.controls == {"c1", "c2", "c3", "c4", "c5", "c6", "c7"}


def test_statuses() -> None:
    assert is_.statuses == {"a", "b", "c", "d", "e", "f"}


def test_max_num_steps() -> None:
    assert is_.max_num_steps == 3


def test_instructions_by_name() -> None:
    assert is_.instructions_by_name == {"i1": i1, "i2": i2}


def test_build_empty_set() -> None:
    assert InstructionSet.Builder().build() == InstructionSet()


def test_build_empty_instruction() -> None:
    assert InstructionSet.Builder().instruction("i").build() == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
            )
        },
    )


def test_build_empty_mode() -> None:
    assert (
        InstructionSet.Builder().instruction("i").mode(AddressingMode.IMMEDIATE).build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.IMMEDIATE,
                        opcode=Byte(0x00),
                    )
                },
            ),
        }
    )


def test_build_empty_mode_str() -> None:
    assert (
        InstructionSet.Builder().instruction("i").mode("absolute").build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                    )
                },
            ),
        }
    )


def test_build_empty_impl() -> None:
    assert InstructionSet.Builder().instruction("i").mode(
        "absolute"
    ).impl().build() == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(),
                        },
                    )
                },
            ),
        }
    )


def test_build_impl_with_statuses() -> None:
    assert InstructionSet.Builder().instruction("i").mode("absolute").impl(
        a=True, b=False
    ).build() == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(
                                statuses={
                                    "a": True,
                                    "b": False,
                                },
                            ),
                        },
                    )
                },
            ),
        }
    )


def test_build_impl_with_empty_step() -> None:
    assert (
        InstructionSet.Builder().instruction("i").mode("absolute").impl().step().build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create(),
                                ],
                            ),
                        },
                    )
                },
            )
        }
    )


def test_build_impl_with_step_directly() -> None:
    assert (
        InstructionSet.Builder()
        .instruction("i")
        .mode("absolute")
        .impl()
        .step("c1")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create({"c1"}),
                                ],
                            ),
                        },
                    )
                },
            )
        }
    )


def test_build_generate_opcodes() -> None:
    assert (
        InstructionSet.Builder()
        .instruction("i")
        .mode("absolute")
        .step("c1")
        .mode("immediate")
        .step("c2")
        .instruction("j")
        .mode("absolute")
        .impl(s1=True)
        .step("c3")
        .impl(s2=True)
        .step("c4")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create({"c1"}),
                                ],
                            ),
                        },
                    ),
                    InstructionMode.create(
                        mode=AddressingMode.IMMEDIATE,
                        opcode=Byte(0x01),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create({"c2"}),
                                ],
                            ),
                        },
                    ),
                },
            ),
            Instruction.create(
                name="j",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x02),
                        impls={
                            InstructionImpl.create(
                                statuses={"s1": True},
                                steps=[
                                    Step.create({"c3"}),
                                ],
                            ),
                            InstructionImpl.create(
                                statuses={"s2": True},
                                steps=[
                                    Step.create({"c4"}),
                                ],
                            ),
                        },
                    ),
                },
            ),
        }
    )


def test_build_step_from_controls() -> None:
    assert (
        InstructionSet.Builder()
        .instruction("i")
        .mode("absolute")
        .step("c1", "c2")
        .step()
        .control("c3")
        .control("c4")
        .step()
        .control("c5")
        .step("c6")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create({"c1", "c2"}),
                                    Step.create({"c3", "c4"}),
                                    Step.create({"c5"}),
                                    Step.create({"c6"}),
                                ],
                            ),
                        },
                    ),
                },
            ),
        }
    )


def test_build_impl_during_step() -> None:
    assert (
        InstructionSet.Builder()
        .instruction("i")
        .mode("absolute")
        .impl(s1=True)
        .step()
        .control("c1")
        .impl(s2=False)
        .step()
        .control("c2")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(
                                statuses={"s1": True},
                                steps=[
                                    Step.create({"c1"}),
                                ],
                            ),
                            InstructionImpl.create(
                                statuses={"s2": False},
                                steps=[
                                    Step.create({"c2"}),
                                ],
                            ),
                        },
                    ),
                },
            ),
        }
    )


def test_build_mode_during_step() -> None:
    assert (
        InstructionSet.Builder()
        .instruction("i")
        .mode("absolute")
        .step()
        .control("c1")
        .mode("immediate")
        .step()
        .control("c2")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create({"c1"}),
                                ],
                            ),
                        },
                    ),
                    InstructionMode.create(
                        mode=AddressingMode.IMMEDIATE,
                        opcode=Byte(0x01),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create({"c2"}),
                                ],
                            ),
                        },
                    ),
                },
            ),
        }
    )


def test_build_instruction_during_step() -> None:
    assert (
        InstructionSet.Builder()
        .instruction("i")
        .mode("absolute")
        .step()
        .control("c1")
        .instruction("j")
        .mode("immediate")
        .step()
        .control("c2")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create({"c1"}),
                                ],
                            ),
                        },
                    ),
                },
            ),
            Instruction.create(
                name="j",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.IMMEDIATE,
                        opcode=Byte(0x01),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create({"c2"}),
                                ],
                            ),
                        },
                    ),
                },
            ),
        }
    )


def test_build_instruction_during_instruction() -> None:
    assert (
        InstructionSet.Builder().instruction("i").instruction("j").build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
            ),
            Instruction.create(
                name="j",
            ),
        }
    )


def test_build_mode_during_mode() -> None:
    assert (
        InstructionSet.Builder()
        .instruction("i")
        .mode("absolute")
        .mode("immediate")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                    ),
                    InstructionMode.create(
                        mode=AddressingMode.IMMEDIATE,
                        opcode=Byte(0x01),
                    ),
                },
            )
        }
    )


def test_build_instruction_during_mode() -> None:
    assert (
        InstructionSet.Builder()
        .instruction("i")
        .mode("absolute")
        .instruction("j")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                    ),
                },
            ),
            Instruction.create(
                name="j",
            ),
        }
    )


def test_with_last_step_controls() -> None:
    for instruction in is_.with_last_step_controls("f1"):
        for mode in instruction:
            for impl in mode:
                assert "f1" in set(list(impl)[-1])
