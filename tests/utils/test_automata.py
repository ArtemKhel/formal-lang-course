import cfpq_data
import pytest
from networkx import MultiDiGraph, is_isomorphic

from project.utils.automata import *
from project.utils.automata import regex_to_dfa
from project.utils.graphs import load_graph_by_name


# noinspection PyTypeChecker
class TestRegexToDFA:
    @staticmethod
    def run(regex: str, accepts: Iterable[Iterable[Symbol]], rejects: Iterable[Iterable[Symbol]]):
        dfa = regex_to_dfa(regex)
        assert dfa.is_deterministic()
        for r in accepts:
            assert dfa.accepts(r)
        for r in rejects:
            assert not dfa.accepts(r)

    def test_empty_regex(self):
        regex = ''
        dfa = regex_to_dfa(regex)
        assert dfa == DeterministicFiniteAutomaton()

    def test_union(self):
        regex = 'abc|d'
        accepts = [['abc'], ['d']]
        rejects = [['abc', 'abc'], ['ab'], ['a', 'b', 'c'], ['abd'], ['dd']]

        self.run(regex, accepts, rejects)

    def test_kleene(self):
        regex = 'a*'
        accepts = ['', ['a'], ['a' for i in range(10)]]
        rejects = [['b'], ['ab'], ['aa']]

        self.run(regex, accepts, rejects)

    def test_concat(self):
        regex = 'Never.gonna.(give.you.up|let.you.down)'
        accepts = ["Never gonna give you up".split(), "Never gonna let you down".split()]
        rejects = ["Never gonna run around and desert you".split()]

        self.run(regex, accepts, rejects)


# noinspection PyTypeChecker
class TestGraphToNFA:
    def test_empty_graph(self):
        expected = NondeterministicFiniteAutomaton()
        actual = graph_to_nfa(MultiDiGraph())
        assert actual.is_equivalent_to(expected)

    def test_cycle_graph(self):
        n = 3
        expected = NondeterministicFiniteAutomaton(states := set(range(n)), start_state=states, final_states=states)
        for i in range(n):
            expected.add_transition(i, 'a', (i + 1) % n)

        actual = graph_to_nfa(cfpq_data.labeled_cycle_graph(n))
        assert actual.is_equivalent_to(expected)

    def test_with_start_and_final_states(self):
        expected = NondeterministicFiniteAutomaton(states := set(range(3)), start_state={0}, final_states={0})
        for i in range(3):
            expected.add_transition(i, chr(ord('a') + i), (i + 1) % 3)

        graph = MultiDiGraph([(0, 1, {'label': 'a'}), (1, 2, {'label': 'b'}), (2, 0, {'label': 'c'})])
        graph.add_node(0, is_start=True, is_final=True)
        actual = graph_to_nfa(graph, start_states={0}, final_states={0})
        assert actual.is_equivalent_to(expected)

    @staticmethod
    def is_isomorphic_nfa_and_graph(nfa: NondeterministicFiniteAutomaton, graph: MultiDiGraph) -> bool:
        nx_graph = nfa.to_networkx()

        for node in filter(lambda node: isinstance(node, str) and node.endswith("_starting"), list(nx_graph)):
            nx_graph.remove_node(node)

        return is_isomorphic(graph, nx_graph)

    def test_graph_from_cfpq(self):
        for name in ('travel', 'skos', 'generations'):
            graph = load_graph_by_name(name)
            nfa = graph_to_nfa(graph)
            assert self.is_isomorphic_nfa_and_graph(nfa, graph)
