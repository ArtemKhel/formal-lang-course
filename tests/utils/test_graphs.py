import filecmp

from cfpq_data import labeled_two_cycles_graph

from project.utils.graphs import *
from tests import TEST_DIR


def test_save_graph(tmp_path):
    expected_file = TEST_DIR / 'utils/resources/expected_two_cycles_graph.dot'
    tmp_file = tmp_path / 'graph.dot'

    graph = labeled_two_cycles_graph(2, 3, labels=('first', 'second'))
    save_graph_as_dot(graph, tmp_file)

    assert filecmp.cmp(tmp_file, expected_file)


def test_get_graph_stats():
    name = "bzip"
    graph = load_graph_by_name(name)
    stats = get_graph_stats(graph)
    assert stats == GraphStats(556, 632, {'a', 'd'}, ['d', 'a'])
