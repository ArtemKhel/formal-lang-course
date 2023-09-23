from pathlib import Path
from typing import NamedTuple

import cfpq_data
import networkx as nx
import pydot


class GraphStats(NamedTuple):
    edges: int
    nodes: int
    edge_labels: set[str]


def load_graph_by_name(name: str) -> nx.MultiDiGraph:
    graph_path = cfpq_data.download(name)
    graph = cfpq_data.graph_from_csv(graph_path)
    return graph


def load_graph_from_dot(path: Path) -> nx.MultiDiGraph:
    return nx.drawing.nx_pydot.from_pydot(pydot.graph_from_dot_file(path)[0])


def load_graph_from_str(strn: str) -> nx.MultiDiGraph:
    return nx.drawing.nx_pydot.from_pydot(pydot.graph_from_dot_data(strn)[0])


def save_graph_as_dot(graph: nx.MultiDiGraph, path: Path):
    nx.drawing.nx_pydot.to_pydot(graph).write(path)


def get_graph_stats(graph: nx.MultiDiGraph) -> GraphStats:
    return GraphStats(
        nodes=graph.number_of_nodes(),
        edges=graph.number_of_edges(),
        edge_labels=set(l for _, _, l in graph.edges.data("label")),
    )


def get_graph_stats_by_name(name: str) -> GraphStats:
    return get_graph_stats(load_graph_by_name(name))


def create_and_save_two_cycles_graph(fst_cycle_len: int, snd_cycle_len: int, labels: tuple[str, str], path: Path):
    save_graph_as_dot(cfpq_data.labeled_two_cycles_graph(fst_cycle_len, snd_cycle_len, labels=labels), path)
