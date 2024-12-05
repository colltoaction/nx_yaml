
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

from .nodes import ScalarNode, MappingNode, SequenceNode

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
        if isinstance(data, ScalarNode):
            data = self.construct_scalar(node)
        if isinstance(data, MappingNode):
            data = self.construct_mapping(node)
        if isinstance(data, SequenceNode):
            data = self.construct_sequence(node)
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
        if not isinstance(node, ScalarNode):
            raise ConstructorError(None, None,
                    "expected a scalar node, but found %s" % node.id,
                    node.start_mark)
        scalar = self.construct_object_at_hyperedge(node.graph, 0)
        return scalar

    def construct_sequence(self, node, deep=False):
        if not isinstance(node, SequenceNode):
            raise ConstructorError(None, None,
                    "expected a sequence node, but found %s" % node.id,
                    node.start_mark)
        sequence = self.construct_object_at_hyperedge(node.graph, 0)
        return sequence

    def construct_mapping(self, node, deep=False):
        if not isinstance(node, MappingNode):
            raise ConstructorError(None, None,
                    "expected a mapping node, but found %s" % node.id,
                    node.start_mark)
        mapping = self.construct_object_at_hyperedge(node.graph, 0)
        return mapping

    def construct_object_at_hyperedge(self, node: nx.MultiGraph, edge=0):
        root = node.nodes[edge]
        assert root["bipartite"] == 0
        root_neighbors = node[edge]
        assert all(node.nodes[n]["bipartite"] == 1 for n in root_neighbors)
        if root["kind"] == "scalar":
            return root["value"]
        if root["kind"] == "sequence":
            ob = []
            assert len(root_neighbors) == 1
            pair_node = next(iter(root_neighbors))
            while pair_node:
                pair_edges = node.edges(pair_node, data="direction")
                assert len(pair_edges) == 2
                pair_edges = iter(pair_edges)
                r1, t1, d1 = next(pair_edges)
                assert (r1, d1) == (pair_node, "head")
                r2, t2, d2 = next(pair_edges)
                assert (r2, d2) == (pair_node, "tail")
                value = self.construct_object_at_hyperedge(node, t2)
                ob.append(value)
                t2_neighbors = iter(node[t2])
                assert pair_node == next(t2_neighbors)
                pair_node = next(t2_neighbors, None)
            return tuple(ob)
        if root["kind"] == "mapping":
            ob = {}
            for pair_node in root_neighbors:
                    # if edge not in (k2, v2) and d2 == "tail":
                pair_edges = node.edges(pair_node)
                assert len(pair_edges) == 3
                pair_edges = iter(pair_edges)
                next(pair_edges) # root
                _, k = next(pair_edges)
                _, v = next(pair_edges)
                key = self.construct_object_at_hyperedge(node, k)
                value = self.construct_object_at_hyperedge(node, v)
                ob[key] = value
            return frozenset(ob.items())
