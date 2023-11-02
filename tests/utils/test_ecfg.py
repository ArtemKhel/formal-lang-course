import pytest

from project.utils.cfg import *
from tests import TEST_DIR
from tests.helpers import load_test_data


@pytest.mark.parametrize(
    ('ecfg_str', 'start', 'expected'),
    [
        ['', 'S', ECFG()],
        [
            '''
            S -> a S b S | $
            ''',
            'S',
            ECFG(variables={Variable('S')}, productions={Variable('S'): Regex('a S b S | $')}),
        ],
        [
            '''
            S -> A B | C
            A -> a* | _
            B -> b* | _
            C -> c*
            ''',
            'S',
            ECFG(
                variables={Variable('S'), Variable('A'), Variable('B'), Variable('C')},
                productions={'S': Regex('A B | C'), 'A': Regex('a* | _'), 'B': Regex('b* | _'), 'C': Regex('c*')},
            ),
        ],
    ],
)
def test_ecfg_from_text(ecfg_str: str, start: str, expected: ECFG):
    actual = ECFG.from_text(ecfg_str)
    assert actual.start_symbol == expected.start_symbol
    assert actual.variables == expected.variables

    assert all(
        actual.productions[var].to_epsilon_nfa().is_equivalent_to(expected.productions[var].to_epsilon_nfa())
        for var in actual.variables
    )
