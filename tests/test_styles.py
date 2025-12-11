import pytest
from pathlib import Path
import networkx as nx
from nx_hif.hif import *
from nx_hif.readwrite import *

from src.nx_yaml import nx_serialize_all, nx_compose_all

@pytest.mark.parametrize("style_file", [
    "style_plain",
    "style_single",
    "style_double",
    "style_literal",
    "style_folded",
    "nulls",
    "map_styles",
    "seq_styles",
    "indicators",
])
def test_styles(style_file):
    expected_yaml = f"tests/resources/yaml/{style_file}.yaml"
    expected_hif = f"tests/resources/hif/{style_file}.json"
    _test_representation_to_native(expected_yaml, expected_hif)

def _test_representation_to_native(expected_yaml, expected_hif):
    original_string = Path(expected_yaml).read_text()
    composed_graph = nx_compose_all(original_string)
    original_graph = read_hif(expected_hif)

    serialized_string = nx_serialize_all(original_graph)
    assert original_string == serialized_string
    assert nx.is_isomorphic(original_graph[2], composed_graph[2])
