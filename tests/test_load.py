import yaml


from src.nx_yaml import NxSafeLoader


def test_null():
    expected_yaml = "tests/resources/yaml/empty.yaml"
    _test_load_nxyaml_dump_yaml(expected_yaml)


def test_single_node():
    expected_yaml = "tests/resources/yaml/single_node.yaml"
    _test_load_nxyaml_dump_yaml(expected_yaml)


def test_two_node_mapping():
    expected_yaml = "tests/resources/yaml/two_node_mapping.yaml"
    _test_load_nxyaml_dump_yaml(expected_yaml)


def test_two_node_list():
    expected_yaml = "tests/resources/yaml/two_node_list.yaml"
    _test_load_nxyaml_dump_yaml(expected_yaml)


def test_mapping_and_list():
    expected_yaml = "tests/resources/yaml/mapping_and_list.yaml"
    _test_load_nxyaml_dump_yaml(expected_yaml)


def test_nested_lists():
    expected_yaml = "tests/resources/yaml/nested_lists.yaml"
    _test_load_nxyaml_dump_yaml(expected_yaml)


def _test_load_nxyaml_dump_yaml(expected_yaml):
    expected_yaml = open(expected_yaml)
    expected_native = yaml.load(expected_yaml, Loader=NxSafeLoader)
    if isinstance(expected_native, frozenset):
        expected_native = dict(expected_native)
    assert yaml.dump(expected_native, Dumper=yaml.SafeDumper)
