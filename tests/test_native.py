import networkx as nx
import matplotlib.pyplot as plt
import yaml

from src.nx_yaml.constructor import NxSafeConstructor
from src.nx_yaml.representer import NxSafeRepresenter


def test_null():
    expected_yaml = "tests/resources/yaml/empty.yaml"
    expected_gml = "tests/resources/networkx/null.gml"
    _test_representation_to_native(expected_yaml, expected_gml)


def test_single_node():
    expected_yaml = "tests/resources/yaml/single_node.yaml"
    expected_gml = "tests/resources/networkx/single_node.gml"
    _test_representation_to_native(expected_yaml, expected_gml)


def test_self_loop():
    expected_yaml = "tests/resources/yaml/self_loop.yaml"
    expected_gml = "tests/resources/networkx/self_loop.gml"
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
    expected_representation = nx.read_gml(expected_gml)
    actual_native = NxSafeConstructor().construct_object(expected_representation)
    backforth_representation = NxSafeRepresenter().represent_data(actual_native)
    assert nx.is_isomorphic(expected_representation, backforth_representation)

    expected_native = yaml.load(open(expected_yaml), Loader=yaml.SafeLoader)
    actual_representation = NxSafeRepresenter().represent_data(expected_native)
    print(expected_native)
    print(actual_representation.nodes(data="value"))
    assert nx.is_isomorphic(expected_representation, actual_representation)
