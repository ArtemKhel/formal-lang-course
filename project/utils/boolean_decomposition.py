from itertools import product
from typing import Dict, Any, Union

from scipy.sparse import dok_matrix, lil_matrix, block_diag, kron, csc_matrix, csr_matrix

from project.utils.automata import *

SparseMatrixType = Union[
    csc_matrix,
    csr_matrix,
    dok_matrix,
    lil_matrix,
]
type_to_name = {
    csc_matrix: 'csc',
    csr_matrix: 'csr',
    dok_matrix: 'dok',
    lil_matrix: 'lil',
}


# noinspection PyTypeChecker
class BooleanDecomposition:
    matrices: Dict[Any, dok_matrix]
    matrix_type: SparseMatrixType
    start_states: SparseMatrixType
    final_states: SparseMatrixType
    n_states: int

    def __init__(self, nfa: NondeterministicFiniteAutomaton | None = None, matrix_type: SparseMatrixType = dok_matrix):
        self.matrix_type = matrix_type
        self.matrices = dict()
        self.states_map = dict()

        if nfa is None:
            self.start_states = matrix_type((1, 0), dtype=bool)
            self.final_states = matrix_type((1, 0), dtype=bool)
            self.n_states = 0
            return

        nfa = nfa.remove_epsilon_transitions()

        self.n_states = len(nfa.states)
        self.states_map = {s: i for i, s in enumerate(nfa.states)}
        self.states_backmap = {i: s for s, i in self.states_map.items()}

        self.start_states = matrix_type((1, self.n_states), dtype=bool)
        for s in nfa.start_states:
            self.start_states[0, self.states_map[s]] = True

        self.final_states = matrix_type((1, self.n_states), dtype=bool)
        for s in nfa.final_states:
            self.final_states[0, self.states_map[s]] = True

        for cur_state, transitions in nfa.to_dict().items():
            for symbol, next_states_set in transitions.items():
                if symbol not in self.matrices.keys():
                    self.matrices[symbol] = matrix_type((self.n_states, self.n_states), dtype=bool)
                if not isinstance(next_states_set, set):
                    next_states_set = {next_states_set}
                for next_state in next_states_set:
                    self.matrices[symbol][self.states_map[cur_state], self.states_map[next_state]] = True

    def to_nfa(self) -> NondeterministicFiniteAutomaton:
        nfa = NondeterministicFiniteAutomaton()
        for label, matrix in self.matrices.items():
            for v, w in zip(*matrix.nonzero()):
                nfa.add_transition(v, label, w)

        for i in self.start_states.nonzero()[1]:
            nfa.add_start_state(i)
        for i in self.final_states.nonzero()[1]:
            nfa.add_final_state(i)

        return nfa.remove_epsilon_transitions()

    def transitive_closure(self) -> 'self.matrix_type':
        if len(self.matrices) == 0:
            return self.matrix_type((self.n_states, self.n_states))
        transitions: 'self.matrix_type' = sum(self.matrices.values())
        prev = 0
        curr = transitions.nnz
        while prev != curr:
            prev = curr
            transitions += transitions @ transitions
            curr = transitions.nnz
        return transitions

    @staticmethod
    def direct_sum(left: 'BooleanDecomposition', right: 'BooleanDecomposition') -> 'BooleanDecomposition':
        res = BooleanDecomposition(matrix_type=left.matrix_type)
        for label in left.matrices.keys() & right.matrices.keys():
            res.matrices[label] = block_diag((left.matrices[label], right.matrices[label]))
        return res


def intersect_nfa(
    nfa_1: NondeterministicFiniteAutomaton,
    nfa_2: NondeterministicFiniteAutomaton,
    matrix_type: SparseMatrixType = dok_matrix,
) -> BooleanDecomposition:
    intersection = BooleanDecomposition(matrix_type=matrix_type)
    bd_1 = BooleanDecomposition(nfa_1, matrix_type=matrix_type)
    bd_2 = BooleanDecomposition(nfa_2, matrix_type=matrix_type)
    intersection.n_states = bd_1.n_states * bd_2.n_states
    common_labels = bd_1.matrices.keys() & bd_2.matrices.keys()

    for label in common_labels:
        intersection.matrices[label] = kron(
            bd_1.matrices[label], bd_2.matrices[label], format=type_to_name[matrix_type]
        )

    intersection.start_states = kron(bd_1.start_states, bd_2.start_states, format=type_to_name[matrix_type])
    intersection.final_states = kron(bd_1.final_states, bd_2.final_states, format=type_to_name[matrix_type])
    intersection.states_map = {
        (s1, s2): (i1 * len(bd_2.states_map) + i2)
        for i, ((s1, i1), (s2, i2)) in enumerate(product(bd_1.states_map.items(), bd_2.states_map.items()))
    }
    intersection.states_backmap = {i: s for s, i in intersection.states_map.items()}

    return intersection
