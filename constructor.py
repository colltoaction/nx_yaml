
__all__ = [
    'NxSafeConstructor',
]

from yaml.constructor import ConstructorError

import types
import networkx as nx

class NxSafeConstructor:

    def __init__(self):
        self.constructed_objects = {}
        self.recursive_objects = {}
        self.state_generators = []

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

    def construct_document(self, node: nx.DiGraph):
        data = self.construct_object(node)
        while self.state_generators:
            state_generators = self.state_generators
            self.state_generators = []
            for generator in state_generators:
                for dummy in generator:
                    pass
        self.constructed_objects = {}
        self.recursive_objects = {}
        return data

    def construct_object(self, node: nx.DiGraph):
        if node in self.constructed_objects:
            return self.constructed_objects[node]
        if node in self.recursive_objects:
            raise ConstructorError(None, None,
                    "found unconstructable recursive node", node.start_mark)
        self.recursive_objects[node] = None
        data = None
        match node.graph.get("kind", None):
            case "scalar": data = self.construct_scalar(node)
            case "sequence": data = self.construct_sequence(node)
            case _: data = self.construct_mapping(node)
        if isinstance(data, types.GeneratorType):
            generator = data
            data = next(generator)
            self.state_generators.append(generator)
        self.constructed_objects[node] = data
        del self.recursive_objects[node]
        return data

    def construct_scalar(self, node: nx.DiGraph):
        """node is a digraph with no annotations"""
        kind = node.graph.get("kind", None)
        if not kind:
            match tuple(iter(node.nodes.items())):
                case ( ): return None
                case ( (value, _), ): return value
        elif kind != "scalar":
            raise ConstructorError(None, None,
                    "expected a scalar node, but found %s" % node.id,
                    node.start_mark)
        value = node.graph.get("value", "")
        return value

    def construct_sequence(self, node: nx.DiGraph):
        return tuple(
            self.construct_object(child)
            for child in node.value)

    def construct_mapping(self, node: nx.DiGraph):
        """"""
        match list(nx.algorithms.cycles.simple_cycles(node)):
            case []:
                match list(node.nodes):
                    case []: return None
                    case [c]: return c
            case [[n]]:
                return n
            case [[c, *o]]:
                return {c: o}
