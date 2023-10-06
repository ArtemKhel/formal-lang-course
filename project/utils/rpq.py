from scipy.sparse import dok_matrix, identity, hstack, vstack

from project.utils.automata import *
from project.utils.boolean_decomposition import BooleanDecomposition, intersect_nfa


def rpq(
    graph: nx.MultiDiGraph,
    regex: str | Regex,
    start_states: set[any] | None = None,
    final_states: set[any] | None = None,
) -> set[tuple[any, any]]:
    graph_fa = graph_to_nfa(graph, start_states, final_states)
    regex_fa = regex_to_dfa(regex)
    intersection = intersect_nfa(graph_fa, regex_fa)
    tc = intersection.transitive_closure()

    res = set()
    for start in intersection.start_states.nonzero()[1]:
        for final in intersection.final_states.nonzero()[1]:
            if tc[start, final]:
                res.add((intersection.states_backmap[start][0], intersection.states_backmap[final][0]))
    return res


def rpq_with_constraint(
    graph: nx.MultiDiGraph,
    regex: str | Regex,
    start_states: set[any] | None = None,
    final_states: set[any] | None = None,
    per_state: bool = False,
) -> set[int] | set[tuple[int, int]]:
    regex = BooleanDecomposition(regex_to_dfa(regex))
    graph = BooleanDecomposition(graph_to_nfa(graph, start_states, final_states))
    if (regex.start_states @ regex.final_states.transpose())[0, 0]:
        for l, m in graph.matrices.items():
            graph.matrices[l] = m + identity(graph.n_states, dtype='bool')

    direct_sum = BooleanDecomposition.direct_sum(regex, graph)

    gsn = len(start_states)
    rn = regex.n_states

    if per_state:
        regex_front = vstack([identity(rn, dtype='bool') for i in range(gsn)])
        graph_front = dok_matrix((rn * gsn, graph.n_states), dtype='bool')
        for i, graph_start_state in enumerate(graph.start_states.nonzero()[1]):
            for start_state in regex.start_states.nonzero()[1]:
                graph_front[i * rn + start_state, graph_start_state] = True

    else:
        regex_front = identity(rn, dtype='bool')
        graph_front = dok_matrix((rn, graph.n_states), dtype='bool')
        for start_state in regex.start_states.nonzero()[1]:
            graph_front[start_state] = graph.start_states
    front = hstack([regex_front, graph_front], format='dok')

    common_labels = graph.matrices.keys() & regex.matrices.keys()
    visited = dok_matrix(front.shape, dtype='bool')
    prev_nnz = None
    curr_nnz = visited.nnz
    while prev_nnz != curr_nnz:
        new_front = dok_matrix(front.shape, dtype='bool')
        for label in common_labels:
            new_subfront = front @ direct_sum.matrices[label]
            for i in range(gsn):
                new_regex_subfront = new_subfront[i * rn : (i + 1) * rn, :rn]
                new_graph_subfront = new_subfront[i * rn : (i + 1) * rn, rn:]

                for x, y in zip(*new_regex_subfront.nonzero()):
                    new_front[i * rn + y] += hstack([new_regex_subfront[x], new_graph_subfront[x]])

        front = new_front
        visited += front
        prev_nnz = curr_nnz
        curr_nnz = visited.nnz

    res = set()
    for i, start_state in enumerate(graph.start_states.nonzero()[1]):
        for regex_state, final_state in zip(*visited[i * rn : (i + 1) * rn, rn:].nonzero()):
            if regex.final_states[0, regex_state] and graph.final_states[0, final_state]:
                if per_state:
                    res.add((graph.states_backmap[start_state], graph.states_backmap[final_state]))
                else:
                    res.add(graph.states_backmap[final_state])

    return res
