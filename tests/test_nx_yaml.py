from pathlib import Path
import networkx as nx
import yaml

from src.nx_yaml import NxSafeDumper, NxSafeLoader, nx_serialize_all, nx_compose_all


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


def test_alias():
    expected_yaml = "tests/resources/yaml/alias.yaml"
    expected_gml = "tests/resources/networkx/alias.gml"
    _test_representation_to_native(expected_yaml, expected_gml)


def test_two_documents():
    expected_yaml = "tests/resources/yaml/two_documents.yaml"
    expected_gml = "tests/resources/networkx/two_documents.gml"
    _test_representation_to_native(expected_yaml, expected_gml)


def test_combination():
    expected_yaml = "tests/resources/yaml/combination.yaml"
    expected_gml = "tests/resources/networkx/combination.gml"
    _test_representation_to_native(expected_yaml, expected_gml)


def _test_representation_to_native(expected_yaml, expected_gml):
    original_string = Path(expected_yaml).read_text()
    composed_graph = nx_compose_all(original_string)
    # out = print_composed_graph_gml(composed_graph)
    # Path(expected_gml).write_text(out)
    original_graph = nx.read_gml(expected_gml)
    serialized_string = nx_serialize_all(original_graph)
    assert original_string == serialized_string
    assert nx.is_isomorphic(original_graph, composed_graph)

def print_composed_graph_gml(composed_graph):
    out = "graph [\n    directed 1"
    for n, d in composed_graph.nodes(data=True):
        out += f"\n    node [\n        id {n}\n        label {n}\n        bipartite {d["bipartite"]}"
        if d.get("kind"):
            out += f"\n        kind \"{d["kind"]}\""
        if d.get("tag"):
            out += f"\n        tag \"{d["tag"]}\""
        if d.get("value"):
            out += f"\n        value \"{d["value"]}\""
        out += f"\n    ]"
    for e0, e1, d in composed_graph.edges(data=True):
        out += f"\n    edge [\n        source {e0}\n        target {e1}\n    ]"
    out += "\n]"
    return out
