import pytest

from project.utils.automata import regex_to_dfa
from project.utils.ecfg import ECFG, ecfg_to_rsm
from project.utils.rsm import RSM
from tests import TEST_DIR
from tests.helpers import load_test_data


class TestRSM:
    @pytest.mark.parametrize(
        ('ecfg',),
        load_test_data(
            TEST_DIR / 'utils/resources/rsm.yaml',
            lambda data: (
                ECFG.from_text(data['ecfg'], start_symbol=start)
                if (start := data.get('start', None))
                else ECFG.from_text(data['ecfg']),
            ),
        ),
    )
    def test_minimize(self, ecfg: ECFG):
        rsm = ecfg_to_rsm(ecfg).minimize()

        assert (
            all(b.dfa == regex_to_dfa(ecfg.productions[b.start_symbol]) for b in rsm.boxes)
            and rsm.start_symbol == ecfg.start_symbol
        )

    def test_empty_cfg(self):
        ecfg = ECFG()
        rsm = ecfg_to_rsm(ecfg)

        assert rsm.start_symbol == "S"
        assert rsm.boxes == []
