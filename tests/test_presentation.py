import networkx as nx
import yaml

from src.nx_yaml import NxSafeLoader


def test_null():
    expected_presentation = "tests/resources/yaml/null.yaml"
    expected_representation = "tests/resources/networkx/null.gml"
    _test_presentation_to_representation(expected_presentation, expected_representation)


def test_single_node():
    expected_presentation = "tests/resources/yaml/single_node.yaml"
    expected_representation = "tests/resources/networkx/single_node.gml"
    _test_presentation_to_representation(expected_presentation, expected_representation)


def test_self_loop():
    expected_presentation = "tests/resources/yaml/self_loop.yaml"
    expected_representation = "tests/resources/networkx/self_loop.gml"
    _test_presentation_to_representation(expected_presentation, expected_representation)


def test_two_node_mapping():
    expected_presentation = "tests/resources/yaml/two_node_mapping.yaml"
    expected_representation = "tests/resources/networkx/two_node_mapping.gml"
    _test_presentation_to_representation(expected_presentation, expected_representation)


def test_nested_lists():
    expected_presentation = "tests/resources/yaml/nested_lists.yaml"
    expected_representation = "tests/resources/networkx/nested_lists.gml"
    _test_presentation_to_representation(expected_presentation, expected_representation)


def _test_presentation_to_representation(expected_yaml, expected_gml):
    expected_presentation = open(expected_yaml)
    expected_presentation = yaml.load(expected_presentation, Loader=NxSafeLoader)
    expected_representation = nx.read_gml(expected_gml)
    actual_representation = open(expected_yaml)
    actual_representation = yaml.compose(actual_representation, Loader=NxSafeLoader)

    # TODO presentation equivalence
    assert nx.is_isomorphic(actual_representation, expected_representation)
