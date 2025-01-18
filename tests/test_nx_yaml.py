from pathlib import Path
import networkx as nx
import yaml

from src.nx_yaml import NxSafeDumper, NxSafeLoader


def test_null():
    expected_yaml = "tests/resources/yaml/null.yaml"
    expected_gml = "tests/resources/networkx/null.gml"
    _test_representation_to_native(expected_yaml, expected_gml)


def test_empty():
    expected_yaml = "tests/resources/yaml/empty.yaml"
    expected_gml = "tests/resources/networkx/empty.gml"
    _test_representation_to_native(expected_yaml, expected_gml)


def test_single_node():
    expected_yaml = "tests/resources/yaml/single_node.yaml"
    expected_gml = "tests/resources/networkx/single_node.gml"
    _test_representation_to_native(expected_yaml, expected_gml)


def test_two_node_mapping():
    expected_yaml = "tests/resources/yaml/two_node_mapping.yaml"
    expected_gml = "tests/resources/networkx/two_node_mapping.gml"
    _test_representation_to_native(expected_yaml, expected_gml)


def test_two_node_list():
    expected_yaml = "tests/resources/yaml/two_node_list.yaml"
    expected_gml = "tests/resources/networkx/two_node_list.gml"
    _test_representation_to_native(expected_yaml, expected_gml)


def test_mapping_and_list():
    expected_yaml = "tests/resources/yaml/mapping_and_list.yaml"
    expected_gml = "tests/resources/networkx/mapping_and_list.gml"
    _test_representation_to_native(expected_yaml, expected_gml)


def test_nested_lists():
    expected_yaml = "tests/resources/yaml/nested_lists.yaml"
    expected_gml = "tests/resources/networkx/nested_lists.gml"
    _test_representation_to_native(expected_yaml, expected_gml)


def _test_representation_to_native(expected_yaml, expected_gml):
    original_graph = nx.read_gml(expected_gml)
    serialized_string = yaml.serialize(original_graph, Dumper=NxSafeDumper)
    original_string = Path(expected_yaml).read_text()
    composed_graph = yaml.compose(original_string, Loader=NxSafeLoader)
    print(composed_graph.nodes(data=True))
    assert original_string == serialized_string
    assert nx.is_isomorphic(original_graph, composed_graph)
