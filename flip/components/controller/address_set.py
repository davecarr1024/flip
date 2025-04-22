import math
from dataclasses import dataclass, field
from typing import Iterable, Iterator, Set, override


@dataclass(frozen=True)
class AddressSet(Set[int]):
    addresses: frozenset[int] = field(default_factory=frozenset[int])

    @override
    def __repr__(self) -> str:
        return f"AddressSet({self.addresses})"

    @override
    def __len__(self) -> int:
        return len(self.addresses)

    @override
    def __iter__(self) -> Iterator[int]:
        yield from self.addresses

    @override
    def __contains__(self, address: object) -> bool:
        return address in self.addresses

    @classmethod
    def num_bits_for_values(cls, values: Iterable[int]) -> int:
        return cls.num_bits_for_value(max(values))

    @classmethod
    def num_bits_for_value(cls, value: int) -> int:
        return math.ceil(math.log2(value))

    def with_values(self, values: Iterable[int], num_bits: int) -> "AddressSet":
        if self.addresses:
            return AddressSet(
                frozenset(
                    {
                        address << num_bits | value
                        for address in self.addresses
                        for value in values
                    }
                )
            )
        else:
            return AddressSet(frozenset(values))

    def with_value(self, value: int, num_bits: int) -> "AddressSet":
        return self.with_values([value], num_bits)

    def with_bits(self, bits: Iterable[bool]) -> "AddressSet":
        return self.with_values([int(bit) for bit in bits], 1)

    def with_bit(self, bit: bool) -> "AddressSet":
        return self.with_values([int(bit)], 1)
