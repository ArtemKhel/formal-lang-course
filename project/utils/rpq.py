from typing import Dict, Any

from pyformlang.finite_automaton import EpsilonNFA
from scipy.sparse import dok_matrix, kron, lil_matrix

from project.utils.automata import *


# noinspection PyTypeChecker
class BooleanDecomposition:
    matrices: Dict[Any, dok_matrix]
    start_states: lil_matrix
    final_states: lil_matrix
    n_states: int
    states_map: dict[int:int]  # TODO: needed only for init

    def __init__(self, nfa: NondeterministicFiniteAutomaton = None):
        # nfa = nfa.remove_epsilon_transitions()
        self.matrices = dict()
        if nfa is not None:
            nfa = nfa.remove_epsilon_transitions()

            self.n_states = len(nfa.states)
            self.states_map = {s: i for i, s in enumerate(nfa.states)}

            self.start_states = lil_matrix((1, self.n_states), dtype=bool)
            for s in nfa.start_states:
                self.start_states[0, self.states_map[s]] = True

            self.final_states = lil_matrix((1, self.n_states), dtype=bool)
            for s in nfa.final_states:
                self.final_states[0, self.states_map[s]] = True

            self.construct_bd_matrix(nfa)
        else:
            self.start_states = lil_matrix((1, 0), dtype=bool)
            self.final_states = dok_matrix((1, 0), dtype=bool)
            self.n_states = 0
            self.states_map = dict()

    def construct_bd_matrix(self, nfa: NondeterministicFiniteAutomaton):
        for cur_state, transitions in nfa.to_dict().items():
            for symbol, next_states_set in transitions.items():
                if symbol not in self.matrices.keys():
                    self.matrices[symbol] = dok_matrix((self.n_states, self.n_states), dtype=bool)
                if not isinstance(next_states_set, set):
                    next_states_set = {next_states_set}
                for next_state in next_states_set:
                    self.matrices[symbol][self.states_map[cur_state], self.states_map[next_state]] = True

    def to_nfa(self) -> NondeterministicFiniteAutomaton:
        enfa = EpsilonNFA()
        for label, matrix in self.matrices.items():
            for (v, w), _ in matrix.items():
                enfa.add_transition(v, label, w)

        for _i, j in zip(*self.start_states.nonzero()):
            enfa.add_start_state(j)
        for _i, j in zip(*self.final_states.nonzero()):
            enfa.add_final_state(j)

        return enfa.remove_epsilon_transitions()

    def transitive_closure(self) -> dok_matrix:
        transitions = sum(self.matrices.values())
        prev = 0
        curr = transitions.nnz
        while prev != curr:
            prev = curr
            transitions += transitions @ transitions
            curr = transitions.nnz
        return transitions


def intersect_nfa(
    nfa_1: NondeterministicFiniteAutomaton, nfa_2: NondeterministicFiniteAutomaton
) -> BooleanDecomposition:
    intersection = BooleanDecomposition()
    bd_1 = BooleanDecomposition(nfa_1)
    bd_2 = BooleanDecomposition(nfa_2)
    intersection.n_states = bd_1.n_states * bd_2.n_states
    common_labels = bd_1.matrices.keys() & bd_2.matrices.keys()

    for label in common_labels:
        intersection.matrices[label] = kron(bd_1.matrices[label], bd_2.matrices[label], format="dok")

    intersection.start_states = kron(bd_1.start_states, bd_2.start_states)
    intersection.final_states = kron(bd_1.final_states, bd_2.final_states)

    return intersection  # .to_nfa()


def rpq(
    graph: nx.MultiDiGraph, regex: str | Regex, start_states: set[int], final_states: set[int]
) -> set[tuple[int, int]]:
    graph_fa = graph_to_nfa(graph, start_states, final_states)
    regex_fa = regex_to_dfa(regex)
    intersection = intersect_nfa(graph_fa, regex_fa)
    tc = intersection.transitive_closure()

    res = set()
    for _, start in zip(*intersection.start_states.nonzero()):
        for _, final in zip(*intersection.final_states.nonzero()):
            if tc[start, final]:
                res.add((start, final))
    return res
