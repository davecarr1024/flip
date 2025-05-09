from enum import Enum, auto


class AddressingMode(Enum):
    NONE = auto()
    IMMEDIATE = auto()
    RELATIVE = auto()
    ZERO_PAGE = auto()
    ABSOLUTE = auto()
    INDEX_X = auto()
    INDEX_Y = auto()
