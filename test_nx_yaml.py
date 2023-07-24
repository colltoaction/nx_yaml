import networkx as nx
import yaml
from yaml import Node

from nx_yaml import to_nx_graph, to_yaml_node


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


def test_loop():
    with open("tests/resources/yaml/loop.yaml", "r") as d:
        expected_node = yaml.compose(d)
        expected_graph = nx.read_gml("tests/resources/networkx/loop.gml")
        graph = to_nx_graph(expected_node)
        node = to_yaml_node(expected_graph)
        assert yaml_nodes_equal(expected_node, node)
        assert nx.utils.graphs_equal(expected_graph, graph)


def yaml_nodes_equal(node1: Node, node2: Node):
    value1 = yaml.constructor.Constructor().construct_document(node1)
    value2 = yaml.constructor.Constructor().construct_document(node2)
    return value1 == value2
