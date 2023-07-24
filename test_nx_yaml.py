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


def test_single_node():
    with open("tests/resources/yaml/single_node.yaml", "r") as d:
        expected_node = yaml.compose(d)
        expected_graph = nx.read_gml("tests/resources/networkx/single_node.gml")
        graph, node = to_nx_graph(expected_node), to_yaml_node(expected_graph)
        assert nx.utils.graphs_equal(expected_graph, graph)
        assert yaml_nodes_equal(expected_node, node)
