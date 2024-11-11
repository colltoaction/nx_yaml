
__all__ = [
    'NxSafeConstructor',
    'FullConstructor',
    'UnsafeConstructor',
    'Constructor',
    'ConstructorError'
]

import networkx as nx
from yaml.error import *

import collections.abc, datetime, base64, binascii, re, sys, types

from nx_yaml.nodes import iter_sequence

class ConstructorError(MarkedYAMLError):
    pass

class NxSafeConstructor:

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
        data = node
        if isinstance(data, nx.Graph):
            if node.graph["kind"] == "scalar":
                data = self.construct_scalar(node)
            elif node.graph["kind"] == "sequence":
                data = self.construct_sequence(node)
            elif node.graph["kind"] == "mapping":
                data = self.construct_mapping(node)
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
        if not node.graph["kind"] == "scalar":
            raise ConstructorError(None, None,
                    "expected a scalar node, but found %s" % node.id,
                    node.start_mark)
        return node.nodes[0]["value"]

    def construct_sequence(self, node, deep=False):
        if not node.graph["kind"] == "sequence":
            raise ConstructorError(None, None,
                    "expected a sequence node, but found %s" % node.id,
                    node.start_mark)
        # read bipartite graph structure
        # which allows us to encode higher-order graphs 
        return tuple(
            self.construct_object(child, deep=deep)
            for child in iter_sequence(node, 0))

    def construct_mapping(self, node, deep=False):
        if not node.graph["kind"] == "mapping":
            raise ConstructorError(None, None,
                    "expected a mapping node, but found %s" % node.id,
                    node.start_mark)
        mapping = self.construct_object_at_hyperedge(node, 0)
        return mapping

    def construct_object_at_hyperedge(self, node: nx.MultiGraph, edge=0):
        # TODO walking the hypergraph with a chosen root recursively
        # or all at once generically.
        # the object is the whole graph
        # and we can't easily extract subgraphs as objects.
        # e.g there can be loops back to the root.
        root = node.nodes[edge]
        if root["kind"] == "scalar":
            scalar = node[edge]
            if scalar:
                return node.nodes[scalar[0]].get("value")
            return None
        if root["kind"] == "sequence":
            ob = []
            for n in node[edge]:
                for u, v, d in node.edges(n, data="direction"):
                    if n == u:
                        ob.append(self.construct_object_at_hyperedge(node, v))
                    elif n == v:
                        ob.append(self.construct_object_at_hyperedge(node, u))
            return tuple(ob)
        if root["kind"] == "mapping":
            ob = {}
            for key in node[edge]:
                for u, v, d in node.edges(key, data="direction"):
                    if u != 0 and v != 0:
                        if u == key:
                            value = self.construct_object_at_hyperedge(node, v)
                        elif v == key:
                            value = self.construct_object_at_hyperedge(node, u)
                        ob[key] = value
            return frozenset(ob.items())
