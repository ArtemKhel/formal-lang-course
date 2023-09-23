import pytest

from project.utils.graphs import load_graph_from_str
from project.utils.rpq import *
from tests import TEST_DIR
from tests.helpers import load_test_data


class TestBooleanDecomposition:
    def test_empty_nfa(self):
        nfa = NondeterministicFiniteAutomaton()
        bd = BooleanDecomposition(nfa)
        assert nfa == bd.to_nfa()

    def test_intersect(self):
        expected = NondeterministicFiniteAutomaton()
        expected.add_start_state(0)
        expected.add_final_state(4)
        expected.add_transition(0, 'a', 0)
        expected.add_transition(0, 'a', 1)
        expected.add_transition(0, 'b', 1)
        expected.add_transition(0, 'b', 3)
        expected.add_transition(3, 'c', 4)
        one = NondeterministicFiniteAutomaton()
        one.add_start_state(0)
        one.add_final_state(1)
        one.add_transition(0, 'a', 0)
        one.add_transition(0, 'b', 0)
        one.add_transition(0, 'b', 1)
        one.add_transition(1, 'c', 1)
        two = NondeterministicFiniteAutomaton()
        two.add_start_state(0)
        two.add_final_state(2)
        two.add_transition(0, 'a', 0)
        two.add_transition(0, 'a', 1)
        two.add_transition(0, 'b', 1)
        two.add_transition(1, 'c', 2)

        assert expected.is_equivalent_to(intersect_nfa(one, two).to_nfa())


class TestRPQ:
    @pytest.mark.parametrize(
        ['graph', 'start_states', 'final_states', 'regex', 'expected'],
        load_test_data(
            TEST_DIR / 'utils/resources/test.yaml',
            lambda data: (
                (
                    load_graph_from_str(data['graph']),
                    set(start) if (start := data.get('start_states')) else None,
                    set(final) if (final := data.get('final_states')) else None,
                    regex,
                    expected,
                )
                for regex, expected in (
                    (req['regex'], set(tuple(x) for x in req['expected'])) for req in data['requests']
                )
            ),
            flat=True,
        ),
    )
    def test_asdf(
        self, graph: nx.MultiDiGraph, start_states: set[int], final_states: set[int], regex: str, expected: set
    ):
        assert rpq(graph, regex, start_states, final_states) == expected
