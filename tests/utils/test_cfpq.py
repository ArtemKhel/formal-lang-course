import networkx as nx
import pytest
from pyformlang.cfg import CFG

from project.utils.graphs import load_graph_from_str
from project.utils.cfpq import cfpq_hellings
from tests import TEST_DIR
from tests.helpers import load_test_data


class TestCFPQ:
    @pytest.mark.parametrize(
        ['graph', 'query', 'start_nodes', 'final_nodes', 'expected'],
        load_test_data(
            TEST_DIR / 'utils/resources/cfpq.yaml',
            lambda data: (
                (
                    load_graph_from_str(data['graph']),
                    #
                    CFG.from_text(text=data['query']['prod'], start_symbol=start)
                    if (start := data['query'].get('start'))
                    else CFG.from_text(text=data['query']['prod']),
                    #
                    set(start) if (start := data.get('start_nodes')) else None,
                    #
                    set(final) if (final := data.get('final_nodes')) else None,
                    #
                    set(tuple(x) for x in data['expected']),
                )
            ),
            # flat=True,
        ),
    )
    def test_asdf(
        self, graph: nx.MultiDiGraph, query: CFG, start_nodes: set[int], final_nodes: set[int], expected: set
    ):
        assert cfpq_hellings(graph, query, start_nodes, final_nodes) == expected
