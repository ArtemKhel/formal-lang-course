from enum import Enum
from typing import Any, Tuple

import networkx as nx
from scipy.sparse import lil_matrix, eye
from pyformlang.cfg import Variable, Terminal, CFG, Epsilon

from project.utils.boolean_decomposition import BooleanDecomposition
from project.utils.cfg import cfg_to_wnf


def _preprocess_cfg(
    cfg: CFG,
) -> Tuple[CFG, set[Variable], dict[Variable, set[Terminal]], dict[Variable, set[tuple[Variable, Variable]]]]:
    cfg = cfg_to_wnf(cfg)
    to_eps: set[Variable] = set()
    to_term: dict[Variable, set[Terminal]] = {}
    to_vars: dict[Variable, set[tuple[Variable, Variable]]] = {}
    for p in cfg.productions:
        match p.body:
            case [Epsilon()] | []:
                to_eps.add(p.head)
            case [Terminal() as t]:
                to_term.setdefault(p.head, set()).add(t)
            case [Variable() as v1, Variable() as v2]:
                to_vars.setdefault(p.head, set()).add((v1, v2))
    return cfg, to_eps, to_term, to_vars


def _hellings(graph: nx.Graph, cfg: CFG) -> set[tuple[Any, Variable, Any]]:
    cfg, to_eps, to_term, to_vars = _preprocess_cfg(cfg)

    res = {(n, eps, n) for n in graph.nodes for eps in to_eps} | {
        (u, term, v) for u, v, l in graph.edges.data("label") for term in to_term if Terminal(l) in to_term[term]
    }

    queue = res.copy()
    while len(queue) > 0:
        start1, v_i, end1 = queue.pop()
        new_res = set()

        for start2, v_j, end2 in filter(lambda x: x[2] == start1, res):
            for v_k in filter(lambda v_k: (v_j, v_i) in to_vars[v_k] and (start2, v_k, end1) not in res, to_vars):
                queue.add((start2, v_k, end1))
                new_res.add((start2, v_k, end1))
        for start2, v_j, end2 in filter(lambda x: x[0] == end1, res):
            for v_k in filter(lambda v_k: (v_i, v_j) in to_vars[v_k] and (start1, v_k, end2) not in res, to_vars):
                queue.add((start1, v_k, end2))
                new_res.add((start1, v_k, end2))

        res |= new_res
    return res


def _matrix(graph: nx.Graph, cfg: CFG) -> set[tuple[Any, Variable, Any]]:
    cfg, to_eps, to_term, to_vars = _preprocess_cfg(cfg)

    n_nodes = len(graph.nodes)
    nodes_map = {n: i for i, n in enumerate(graph.nodes)}
    nodes_backmap = {i: n for i, n in enumerate(graph.nodes)}
    boolean_decomposition: dict[Variable, lil_matrix] = {
        v: lil_matrix((n_nodes, n_nodes), dtype=bool) for v in cfg.variables
    }

    for u, v, label in graph.edges.data('label'):
        for var in to_term:
            if Terminal(label) in to_term[var]:
                i, j = nodes_map[u], nodes_map[v]
                boolean_decomposition[var][i, j] = True

    diag = eye(n_nodes, n_nodes, dtype=bool)
    for var in to_eps:
        boolean_decomposition[var] += diag

    changing = True
    while changing:
        changing = False
        for head in to_vars.keys():
            for body1, body2 in to_vars[head]:
                prev = boolean_decomposition[head].nnz
                boolean_decomposition[head] += boolean_decomposition[body1] @ boolean_decomposition[body2]
                curr = boolean_decomposition[head].nnz
                changing |= prev != curr

    result = set()
    for v, adj in boolean_decomposition.items():
        for i, j in zip(*adj.nonzero()):
            result.add((nodes_backmap[i], v, nodes_backmap[j]))
    return result


class CFPQ_Algorithm(Enum):
    Hellings = _hellings
    Matrix = _matrix


def cfpq(
    algorithm: CFPQ_Algorithm,
    graph: nx.MultiDiGraph,
    query: CFG,
    start_nodes: set[Any] | None = None,
    final_nodes: set[Any] | None = None,
) -> set[tuple[Any, Any]]:
    if start_nodes is None:
        start_nodes = set(graph.nodes)
    if final_nodes is None:
        final_nodes = set(graph.nodes)

    transitive_closure = algorithm(graph, query)

    return {
        (start, final)
        for start, var, final in transitive_closure
        if start in start_nodes and var == query.start_symbol and final in final_nodes
    }
