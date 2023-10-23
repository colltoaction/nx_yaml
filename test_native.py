import io
import networkx as nx
import yaml

from . import NxSafeDumper, NxSafeLoader


def test_null():
    expected_yaml = "tests/resources/yaml/empty.yaml"
    expected_gml = "tests/resources/networkx/null.gml"
    _test_node_to_native(expected_yaml, expected_gml)


def _test_node_to_native(expected_yaml, expected_gml):
    expected_native = open(expected_yaml)
    expected_native = yaml.load(expected_native, Loader=NxSafeLoader)
    expected_representation = nx.read_gml(expected_gml)

    dumper = NxSafeDumper(io.StringIO())
    dumper.open()
    actual_representation = dumper.represent_data(expected_native)

    actual_native = NxSafeLoader(io.StringIO()).construct_document(expected_representation)

    assert actual_native == expected_native
    assert nx.is_isomorphic(actual_representation, expected_representation)


# def test_single_node():
#     with open("tests/resources/yaml/single_node.yaml", "r") as d:
#         expected = yaml.compose(d, Loader=NxSafeLoader)
#         actual = nx.read_gml("tests/resources/networkx/single_node.gml")
#         actual = yaml.serialize(d, Dumper=NxSafeDumper)
#         assert nx.utils.graphs_equal(actual, expected)


# def test_loop():
#     with open("tests/resources/yaml/loop.yaml", "r") as d:
#         expected = yaml.compose(d, Loader=NxSafeLoader)
#         actual = nx.read_gml("tests/resources/networkx/loop.gml")
#         actual = yaml.serialize(d, Dumper=NxSafeDumper)
#         assert nx.utils.graphs_equal(actual, expected)
