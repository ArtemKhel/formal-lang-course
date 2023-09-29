from itertools import product
from typing import Dict, Any

from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from scipy.sparse import dok_matrix, lil_matrix, block_diag, kron

from project.utils.automata import *


# noinspection PyTypeChecker
class BooleanDecomposition:
    matrices: Dict[Any, dok_matrix]
    start_states: lil_matrix
    final_states: lil_matrix
    n_states: int

    def __init__(self, nfa: NondeterministicFiniteAutomaton | None = None):
        self.matrices = dict()
        self.states_map = dict()

        if nfa is None:
            self.start_states = lil_matrix((1, 0), dtype=bool)
            self.final_states = dok_matrix((1, 0), dtype=bool)
            self.n_states = 0
            return

        nfa = nfa.remove_epsilon_transitions()

        self.n_states = len(nfa.states)
        self.states_map = {s: i for i, s in enumerate(nfa.states)}
        self.states_backmap = {i: s for s, i in self.states_map.items()}

        self.start_states = lil_matrix((1, self.n_states), dtype=bool)
        for s in nfa.start_states:
            self.start_states[0, self.states_map[s]] = True

        self.final_states = lil_matrix((1, self.n_states), dtype=bool)
        for s in nfa.final_states:
            self.final_states[0, self.states_map[s]] = True

        for cur_state, transitions in nfa.to_dict().items():
            for symbol, next_states_set in transitions.items():
                if symbol not in self.matrices.keys():
                    self.matrices[symbol] = dok_matrix((self.n_states, self.n_states), dtype=bool)
                if not isinstance(next_states_set, set):
                    next_states_set = {next_states_set}
                for next_state in next_states_set:
                    self.matrices[symbol][self.states_map[cur_state], self.states_map[next_state]] = True

    def to_nfa(self) -> NondeterministicFiniteAutomaton:
        nfa = NondeterministicFiniteAutomaton()
        for label, matrix in self.matrices.items():
            for (v, w), _ in matrix.items():
                nfa.add_transition(v, label, w)

        for i in self.start_states.nonzero()[1]:
            nfa.add_start_state(i)
        for i in self.final_states.nonzero()[1]:
            nfa.add_final_state(i)

        return nfa.remove_epsilon_transitions()

    def transitive_closure(self) -> dok_matrix:
        if len(self.matrices) == 0:
            return dok_matrix((self.n_states, self.n_states))
        transitions: dok_matrix = sum(self.matrices.values())
        prev = 0
        curr = transitions.nnz
        while prev != curr:
            prev = curr
            transitions += transitions @ transitions
            curr = transitions.nnz
        return transitions

    @staticmethod
    def direct_sum(left: 'BooleanDecomposition', right: 'BooleanDecomposition') -> 'BooleanDecomposition':
        res = BooleanDecomposition()
        for label in left.matrices.keys() & right.matrices.keys():
            res.matrices[label] = block_diag((left.matrices[label], right.matrices[label]))
        return res


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
    intersection.states_map = {
        (s1, s2): (i1 * len(bd_2.states_map) + i2)
        for i, ((s1, i1), (s2, i2)) in enumerate(product(bd_1.states_map.items(), bd_2.states_map.items()))
    }
    intersection.states_backmap = {i: s for s, i in intersection.states_map.items()}

    return intersection
