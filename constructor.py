
__all__ = [
    'NxSafeConstructor',
]

from yaml.constructor import ConstructorError

import collections.abc, types

class NxSafeConstructor:

    yaml_constructors = {}
    yaml_multi_constructors = {}

    def __init__(self):
        self.constructed_objects = {}
        self.recursive_objects = {}
        self.state_generators = []
        self.deep_construct = False

    def check_data(self):
        # If there are more documents available?
        return self.check_node()

    def check_state_key(self, key):
        """Block special attributes/methods from being set in a newly created
        object, to prevent user-controlled methods from being called during
        deserialization"""
        if self.get_state_keys_blacklist_regexp().match(key):
            raise ConstructorError(None, None,
                "blacklisted key '%s' in instance state found" % (key,), None)

    def get_data(self):
        # Construct and return the next document.
        if self.check_node():
            return self.construct_document(self.get_node())

    def get_single_data(self):
        # Ensure that the stream contains a single document and construct it.
        node = self.get_single_node()
        if node is not None:
            return self.construct_document(node)
        return None

    def construct_document(self, node):
        data = self.construct_object(node)
        while self.state_generators:
            state_generators = self.state_generators
            self.state_generators = []
            for generator in state_generators:
                for dummy in generator:
                    pass
        self.constructed_objects = {}
        self.recursive_objects = {}
        self.deep_construct = False
        return data

    def construct_object(self, node, deep=False):
        if node in self.constructed_objects:
            return self.constructed_objects[node]
        if deep:
            old_deep = self.deep_construct
            self.deep_construct = True
        if node in self.recursive_objects:
            raise ConstructorError(None, None,
                    "found unconstructable recursive node", node.start_mark)
        self.recursive_objects[node] = None
        constructor = None
        kind = node.graph["kind"] if "kind" in node.graph else "scalar"
        if kind == "scalar":
            constructor = self.__class__.construct_scalar
        elif kind == "sequence":
            constructor = self.__class__.construct_sequence
        elif kind == "mapping":
            constructor = self.__class__.construct_mapping
        data = constructor(self, node)
        if isinstance(data, types.GeneratorType):
            generator = data
            data = next(generator)
            if self.deep_construct:
                for dummy in generator:
                    pass
            else:
                self.state_generators.append(generator)
        self.constructed_objects[node] = data
        del self.recursive_objects[node]
        if deep:
            self.deep_construct = old_deep
        return data

    def construct_scalar(self, node):
        kind = node.graph["kind"] if "kind" in node.graph else "scalar"
        if kind != "scalar":
            raise ConstructorError(None, None,
                    "expected a scalar node, but found %s" % node.id,
                    node.start_mark)
        value = node.graph["value"] if "value" in node.graph else ""
        return value

    def construct_sequence(self, node, deep=False):
        if node.kind != "sequence":
            raise ConstructorError(None, None,
                    "expected a sequence node, but found %s" % node.id,
                    node.start_mark)
        return tuple(self.construct_object(child, deep=deep)
                for child in node.value)

    def construct_mapping(self, node, deep=False):
        assert False
        if node.kind != "mapping":
            raise ConstructorError(None, None,
                    "expected a mapping node, but found %s" % node.id,
                    node.start_mark)

        self.flatten_mapping(node)

        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, collections.abc.Hashable):
                raise ConstructorError("while constructing a mapping", node.start_mark,
                        "found unhashable key", key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

    def flatten_mapping(self, node):
        merge = []
        index = 0
        while index < len(node.value):
            key_node, value_node = node.value[index]
            if key_node.tag == 'tag:yaml.org,2002:merge':
                del node.value[index]
                if value_node.kind == "mapping":
                    self.flatten_mapping(value_node)
                    merge.extend(value_node.value)
                elif value_node.kind == "sequence":
                    submerge = []
                    for subnode in value_node.value:
                        if subnode.kind != "mapping":
                            raise ConstructorError("while constructing a mapping",
                                    node.start_mark,
                                    "expected a mapping for merging, but found %s"
                                    % subnode.id, subnode.start_mark)
                        self.flatten_mapping(subnode)
                        submerge.append(subnode.value)
                    submerge.reverse()
                    for value in submerge:
                        merge.extend(value)
                else:
                    raise ConstructorError("while constructing a mapping", node.start_mark,
                            "expected a mapping or list of mappings for merging, but found %s"
                            % value_node.id, value_node.start_mark)
            elif key_node.tag == 'tag:yaml.org,2002:value':
                key_node.tag = 'tag:yaml.org,2002:str'
                index += 1
            else:
                index += 1
        if merge:
            node.value = merge + node.value
