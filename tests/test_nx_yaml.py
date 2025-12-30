import pytest
from pathlib import Path
import networkx as nx
from nx_hif.hif import *
from nx_hif.readwrite import *

from src.nx_yaml import nx_serialize_all, nx_compose_all

@pytest.mark.parametrize("name", [
    "empty",
    "single_node",
    "two_node_mapping",
    "two_node_list",
    "mapping_and_list",
    "nested_lists",
    "alias",
    "two_documents",
    "scanner_directives",
])
def test_nx_yaml(name):
    expected_yaml = f"tests/resources/yaml/{name}.yaml"
    expected_hif = f"tests/resources/hif/{name}.json"
    _test_representation_to_native(expected_yaml, expected_hif)


def _test_representation_to_native(expected_yaml, expected_hif):
    original_string = Path(expected_yaml).read_text()
    composed_graph = nx_compose_all(original_string)
    original_graph = read_hif(expected_hif)
    og = {frozenset(ee) for ee in original_graph[2].edges}
    cg = {frozenset(ee) for ee in composed_graph[2].edges}
    # print(og)
    # print(cg)
    # print(*og.difference(cg), sep="\n")
    # print()
    # print(*cg.difference(og), sep="\n")
    serialized_string = nx_serialize_all(original_graph)

    # Normalizing potential newline differences if needed, but keeping simple for now
    # The existing tests used exact match, so we continue with that.
    assert original_string == serialized_string
    assert nx.is_isomorphic(original_graph[2], composed_graph[2])
