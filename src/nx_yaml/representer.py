
__all__ = ['NxSafeRepresenter']

import itertools
import networkx as nx

class NxSafeRepresenter:


    def __init__(self, default_style=None, default_flow_style=False, sort_keys=True):
        self.default_style = default_style
        self.sort_keys = sort_keys
        self.default_flow_style = default_flow_style
        self.represented_objects = {}
        self.object_keeper = []
        self.alias_key = None

    def represent(self, data):
        node = self.represent_data(data)
        self.serialize(node)
        self.represented_objects = {}
        self.object_keeper = []
        self.alias_key = None

    def represent_data(self, data) -> nx.DiGraph:
        self.alias_key = id(data)
        if self.alias_key is not None:
            if self.alias_key in self.represented_objects:
                node = self.represented_objects[self.alias_key]
                #if node is None:
                #    raise RepresenterError("recursive objects are not allowed: %r" % data)
                return node
            #self.represented_objects[alias_key] = None
            self.object_keeper.append(data)

        node = nx.DiGraph()
        match data:
            case None: node.graph["kind"] = "scalar"
            case str(value):
                node = self.represent_scalar(value)
            case tuple(values) | list(values):
                node = self.represent_sequence(values)
            case dict(key_values):
                node = self.represent_mapping(key_values)
        return node

    def represent_scalar(self, value) -> nx.DiGraph:
        node = nx.DiGraph(kind='scalar', value=value)
        node.add_node(value)
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        return node

    def represent_sequence(self, sequence) -> nx.DiGraph:
        node = nx.DiGraph(kind='sequence')
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        sequence = list(map(self.represent_data, sequence))
        if len(sequence) == 1:
            data = sequence[0]
            node.add_nodes_from(data)
            sle = nx.selfloop_edges(data)
            node.add_edges_from(sle)

        sequence = itertools.pairwise(sequence)
        for node_key, node_value in sequence:
            node.update(edges=node_key.edges, nodes=node_key.nodes)
            node.update(edges=node_value.edges, nodes=node_value.nodes)
            node.add_edges_from(
                itertools.product(
                    (n for n, d in node_key.in_degree() if d == 0),
                    (n for n, d in node_value.in_degree() if d == 0)))
        return node

    def represent_mapping(self, mapping: dict) -> nx.DiGraph:
        node = nx.DiGraph(kind='mapping')
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        for item_key, item_value in mapping.items():
            node_key = self.represent_data(item_key)
            node_value = self.represent_data(item_value)
            node.update(edges=node_key.edges, nodes=node_key.nodes)
            node.update(edges=node_value.edges, nodes=node_value.nodes)
            node.add_edges_from(
                itertools.product(
                    (n for n, d in node_key.in_degree() if d == 0),
                    (n for n, d in node_value.in_degree() if d == 0)))
        return node
