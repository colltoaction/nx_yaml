from pathlib import Path
import networkx as nx
from nx_hif.hif import *
from nx_hif.readwrite import *

from src.nx_yaml import nx_serialize_all, nx_compose_all


def test_empty():
    expected_yaml = "tests/resources/yaml/empty.yaml"
    expected_hif = "tests/resources/hif/empty.json"
    _test_representation_to_native(expected_yaml, expected_hif)


def test_single_node():
    expected_yaml = "tests/resources/yaml/single_node.yaml"
    expected_hif = "tests/resources/hif/single_node.json"
    _test_representation_to_native(expected_yaml, expected_hif)


def test_two_node_mapping():
    expected_yaml = "tests/resources/yaml/two_node_mapping.yaml"
    expected_hif = "tests/resources/hif/two_node_mapping.json"
    _test_representation_to_native(expected_yaml, expected_hif)


def test_two_node_list():
    expected_yaml = "tests/resources/yaml/two_node_list.yaml"
    expected_hif = "tests/resources/hif/two_node_list.json"
    _test_representation_to_native(expected_yaml, expected_hif)


def test_mapping_and_list():
    expected_yaml = "tests/resources/yaml/mapping_and_list.yaml"
    expected_hif = "tests/resources/hif/mapping_and_list.json"
    _test_representation_to_native(expected_yaml, expected_hif)


def test_nested_lists():
    expected_yaml = "tests/resources/yaml/nested_lists.yaml"
    expected_hif = "tests/resources/hif/nested_lists.json"
    _test_representation_to_native(expected_yaml, expected_hif)


def test_alias():
    expected_yaml = "tests/resources/yaml/alias.yaml"
    expected_hif = "tests/resources/hif/alias.json"
    _test_representation_to_native(expected_yaml, expected_hif)


def test_two_documents():
    expected_yaml = "tests/resources/yaml/two_documents.yaml"
    expected_hif = "tests/resources/hif/two_documents.json"
    _test_representation_to_native(expected_yaml, expected_hif)


def test_combination():
    expected_yaml = "tests/resources/yaml/combination.yaml"
    expected_hif = "tests/resources/hif/combination.json"
    _test_representation_to_native(expected_yaml, expected_hif)


def test_tags():
    expected_yaml = "tests/resources/yaml/tags.yaml"
    expected_hif = "tests/resources/hif/tags.json"
    _test_representation_to_native(expected_yaml, expected_hif)


def test_tags_2():
    expected_yaml = "tests/resources/yaml/tags_2.yaml"
    expected_hif = "tests/resources/hif/tags_2.json"
    _test_representation_to_native(expected_yaml, expected_hif)


def _test_representation_to_native(expected_yaml, expected_hif):
    original_string = Path(expected_yaml).read_text()
    composed_graph = nx_compose_all(original_string)
    original_graph = read_hif(expected_hif)
    serialized_string = nx_serialize_all(original_graph)
    assert original_string == serialized_string
    assert nx.is_isomorphic(original_graph[2], composed_graph[2])
