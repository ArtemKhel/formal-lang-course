from typing import Any

import networkx as nx
from pyformlang.cfg import Variable, Terminal, CFG, Epsilon

from project.utils.cfg import cfg_to_wnf


def hellings(graph: nx.Graph, cfg: CFG) -> set[tuple[Any, Variable, Any]]:
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

    res = {(n, eps, n) for n in graph.nodes for eps in to_eps} | {
        (u, term, v) for u, v, l in graph.edges.data("label") for term in to_term if Terminal(l) in to_term[term]
    }

    queue = res.copy()
    while len(queue) > 0:
        start1, v_i, end1 = queue.pop()

        _res = set()
        for start2, v_j, end2 in filter(lambda x: x[2] == start1, res):
            for v_k in filter(lambda v_k: (v_j, v_i) in to_vars[v_k] and (start2, v_k, end1) not in res, to_vars):
                queue.add((start2, v_k, end1))
                _res.add((start2, v_k, end1))
        for start2, v_j, end2 in filter(lambda x: x[0] == end1, res):
            for v_k in filter(lambda v_k: (v_i, v_j) in to_vars[v_k] and (start1, v_k, end2) not in res, to_vars):
                queue.add((start1, v_k, end2))
                _res.add((start1, v_k, end2))

        res |= _res
    return res


def cfpq_hellings(
    graph: nx.MultiDiGraph, query: CFG, start_nodes: set[Any] | None = None, final_nodes: set[Any] | None = None
) -> set[tuple[Any, Any]]:
    if start_nodes is None:
        start_nodes = set(graph.nodes)
    if final_nodes is None:
        final_nodes = set(graph.nodes)

    transitive_closure = hellings(graph, query)

    return {
        (start, final)
        for start, var, final in transitive_closure
        if start in start_nodes and var == query.start_symbol and final in final_nodes
    }


if __name__ == '__main__':

    def _create_graph(nodes, edges) -> nx.MultiDiGraph:
        graph = nx.MultiDiGraph()
        graph.add_nodes_from(nodes)
        graph.add_edges_from(list(map(lambda edge: (edge[0], edge[2], {"label": edge[1]}), edges)))
        return graph

    res = cfpq_hellings(
        query=CFG.from_text(
            """
                S -> A B
                A -> a
                B -> b
            """
        ),
        graph=_create_graph(nodes=[0, 1, 2], edges=[(0, "a", 1), (1, "b", 2)]),
        start_var='S',
    )
    print(res)
