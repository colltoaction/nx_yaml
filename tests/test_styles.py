
from pathlib import Path
import networkx as nx
from nx_hif.hif import *
from nx_hif.readwrite import *

from src.nx_yaml import nx_serialize_all, nx_compose_all

def test_style_plain():
    _test_style("style_plain")

def test_style_single():
    _test_style("style_single")

def test_style_double():
    _test_style("style_double")

def test_style_literal():
    _test_style("style_literal")

def test_style_folded():
    _test_style("style_folded")

def test_nulls():
    _test_style("nulls")

def _test_style(name):
    expected_yaml = f"tests/resources/yaml/{name}.yaml"
    expected_hif = f"tests/resources/hif/{name}.json"
    _test_representation_to_native(expected_yaml, expected_hif)

def _test_representation_to_native(expected_yaml, expected_hif):
    original_string = Path(expected_yaml).read_text()
    composed_graph = nx_compose_all(original_string)
    original_graph = read_hif(expected_hif)

    serialized_string = nx_serialize_all(original_graph)
    assert original_string == serialized_string
    assert nx.is_isomorphic(original_graph[2], composed_graph[2])
