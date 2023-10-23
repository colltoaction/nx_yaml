import io
import networkx as nx
import yaml

from . import NxSafeDumper, NxSafeLoader


def test_null():
    expected_native = open("tests/resources/yaml/empty.yaml")
    expected_native = yaml.load(expected_native, Loader=NxSafeLoader)
    expected_representation = nx.read_gml("tests/resources/networkx/null.gml")

    dumper = NxSafeDumper(io.StringIO())
    dumper.open()
    actual_representation = dumper.represent_data(expected_native)

    actual_native = NxSafeLoader(io.StringIO()).construct_object(expected_representation)

    assert actual_native == expected_native
    assert nx.is_isomorphic(actual_representation, expected_representation)
