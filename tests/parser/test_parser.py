import pytest

from project.parser.parser import *
from tests import TEST_DIR
from tests.helpers import load_test_data


class TestRSM:
    @pytest.mark.parametrize(
        ('code', 'should_fail'),
        load_test_data(
            TEST_DIR / 'parser/resources/parser.yaml', lambda data: (data['code'], data.get('should_fail', False))
        ),
    )
    def test_parser(self, code: str, should_fail: bool):
        assert check_correctness(code) != should_fail
