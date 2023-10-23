import io
import networkx as nx
import yaml

from . import NxSafeDumper, NxSafeLoader


def test_null():
    expected_presentation = open("tests/resources/yaml/empty.yaml")
    expected_presentation = yaml.load(expected_presentation, Loader=NxSafeLoader)
    expected_representation = nx.read_gml("tests/resources/networkx/null.gml")
    actual_presentation = yaml.serialize(expected_representation, Dumper=NxSafeDumper)
    actual_representation = yaml.compose(open("tests/resources/yaml/empty.yaml"), Loader=NxSafeLoader)

    # TODO presentation equivalence
    # assert actual_presentation == expected_presentation
    assert nx.utils.graphs_equal(actual_representation, expected_representation)


# def test_single_node():
#     with open("tests/resources/yaml/single_node.yaml", "r") as d:
#         actual = yaml.compose(d, Loader=NxSafeLoader)
#         expected = nx.read_gml("tests/resources/networkx/single_node.gml")
#         assert nx.utils.graphs_equal(actual, expected)


# def test_loop():
#     with open("tests/resources/yaml/loop.yaml", "r") as d:
#         actual = yaml.compose(d, Loader=NxSafeLoader)
#         expected = nx.read_gml("tests/resources/networkx/loop.gml")
#         assert nx.utils.graphs_equal(actual, expected)
