import networkx as nx
import yaml

from nx_yaml import to_nx_graph, to_yaml_node, yaml_nodes_equal


def test_null():
    with open("tests/resources/yaml/empty.yaml", "r") as d:
        expected_node = yaml.compose(d)
        expected_graph = nx.read_gml("tests/resources/networkx/null.gml")
        graph, node = to_nx_graph(expected_node), to_yaml_node(expected_graph)
        assert nx.utils.graphs_equal(expected_graph, graph)
        assert yaml_nodes_equal(expected_node, node)


def test_singleton():
    document = "false"
    digraph = doc_digraph(document)
    assert list(digraph.nodes) == [False]
    assert list(digraph.edges) == []


def doc_digraph(document: str, graph: str):
    with open(document, "r") as d, open(graph, "r") as g:
        yaml_node = yaml.compose(d)
        nx_graph = nx.read_gml(g)
        return to_nx_graph(yaml_node), to_yaml_node(nx_graph)
