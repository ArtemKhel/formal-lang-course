import pytest

from project.utils.cfg import *
from tests import TEST_DIR
from tests.helpers import load_test_data


@pytest.mark.parametrize(
    ('cfg', 'expected'),
    load_test_data(
        TEST_DIR / 'utils/resources/cfg.yaml',
        lambda data: (
            CFG.from_text(data['cfg'], start_symbol=start)
            if (start := data.get('start'))
            else CFG.from_text(data['cfg']),
            CFG.from_text(data['expected']),
        ),
    ),
)
def test_cfg_to_wnf(cfg: CFG, expected: CFG):
    wnf = cfg_to_wnf(cfg)
    assert is_weak_normal_form(wnf)
    assert cfgs_are_equivalent(wnf, expected)
