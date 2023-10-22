import networkx as nx
import yaml

from . import NxSafeLoader


def test_null():
    with open("tests/resources/yaml/empty.yaml", "r") as d:
        actual = yaml.compose(d, Loader=NxSafeLoader)
        expected = nx.read_gml("tests/resources/networkx/null.gml")
        assert nx.utils.graphs_equal(actual, expected)


def test_single_node():
    with open("tests/resources/yaml/single_node.yaml", "r") as d:
        actual = yaml.compose(d, Loader=NxSafeLoader)
        expected = nx.read_gml("tests/resources/networkx/single_node.gml")
        assert nx.utils.graphs_equal(actual, expected)


def test_loop():
    with open("tests/resources/yaml/loop.yaml", "r") as d:
        actual = yaml.compose(d, Loader=NxSafeLoader)
        expected = nx.read_gml("tests/resources/networkx/loop.gml")
        assert nx.utils.graphs_equal(actual, expected)
