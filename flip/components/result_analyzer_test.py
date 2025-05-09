from pytest_subtests import SubTests

from flip.bytes import Byte
from flip.components import Bus, ResultAnalyzer


def test_result_analyzer(subtests: SubTests) -> None:
    for value, zero, negative in list[
        tuple[
            Byte,
            bool,
            bool,
        ]
    ](
        [
            (Byte(0), True, False),
            (Byte(1), False, False),
            (Byte(0x7F), False, False),
            (Byte(0x80), False, True),
        ]
    ):
        with subtests.test(value=value, zero=zero, negative=negative):
            result_analyzer = ResultAnalyzer(name="result_analyzer", bus=Bus())
            result_analyzer.value = value
            result_analyzer.tick()
            assert result_analyzer.zero == zero
            assert result_analyzer.negative == negative
