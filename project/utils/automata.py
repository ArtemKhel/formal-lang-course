from typing import Iterable

import networkx as nx
from pyformlang.finite_automaton import DeterministicFiniteAutomaton, NondeterministicFiniteAutomaton
from pyformlang.regular_expression import Regex


def regex_to_dfa(regex: str | Regex) -> DeterministicFiniteAutomaton:
    if isinstance(regex, str):
        regex = Regex(regex)
    return regex.to_epsilon_nfa().minimize()


def graph_to_nfa(
    graph: nx.MultiDiGraph, start_states: Iterable[any] = None, final_states: Iterable[any] = None
) -> NondeterministicFiniteAutomaton:
    nfa = NondeterministicFiniteAutomaton()

    for v, w, label in graph.edges.data('label'):
        nfa.add_transition(v, label, w)

    for v in start_states if start_states is not None else graph.nodes:
        nfa.add_start_state(v)
    for v in final_states if final_states is not None else graph.nodes:
        nfa.add_final_state(v)

    return nfa
