from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Result:
    value: "byte.Byte"
    carry: bool = False  # Set if result > 255 (unsigned overflow)
    zero: bool = False  # Set if result == 0
    negative: bool = False  # Set if bit 7 (MSB) is 1
    overflow: bool = False  # Set if signed overflow (see rule below)
    half_carry: bool = False  # Set if carry from bit 3 to bit 4 (BCD)

    def __repr__(self) -> str:
        flags = list[str]()
        if self.carry:
            flags.append("C")
        if self.zero:
            flags.append("Z")
        if self.negative:
            flags.append("N")
        if self.overflow:
            flags.append("V")
        if self.half_carry:
            flags.append("H")
        return f"<{self.value!r} {' '.join(flags)}>"


from flip.bytes import byte
