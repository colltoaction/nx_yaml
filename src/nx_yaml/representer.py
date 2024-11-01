
__all__ = ['BaseRepresenter', 'NxSafeRepresenter',
    'RepresenterError']

from itertools import pairwise
import networkx as nx
from yaml.error import *

import datetime, copyreg, types, base64, collections

class RepresenterError(YAMLError):
    pass

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

    def represent_data(self, data):
        if self.ignore_aliases(data):
            self.alias_key = None
        else:
            self.alias_key = id(data)
        if self.alias_key is not None:
            if self.alias_key in self.represented_objects:
                node = self.represented_objects[self.alias_key]
                #if node is None:
                #    raise RepresenterError("recursive objects are not allowed: %r" % data)
                return node
            #self.represented_objects[alias_key] = None
            self.object_keeper.append(data)
        data_types = type(data).__mro__
        if data_types[0] == dict:
            node = self.represent_mapping('tag:yaml.org,2002:map', data)
        elif data_types[0] == list:
            node = self.represent_sequence('tag:yaml.org,2002:seq', data)
        else:
            node = self.represent_scalar('tag:yaml.org,2002:str', str(data))
                    
        #if alias_key is not None:
        #    self.represented_objects[alias_key] = node
        return node

    def represent_scalar(self, tag, value, style=None):
        if style is None:
            style = self.default_style
        node = nx.MultiGraph(kind="scalar", tag=tag, value=value, style=style)
        node.add_node(0, bipartite=0, tag=tag, value=value)
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        return node

    def represent_sequence(self, tag, sequence, flow_style=None):
        node = nx.MultiGraph(kind="sequence", tag=tag, flow_style=flow_style)
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        best_style = True
        relabel_label = 0
        data = []
        for item in sequence:
            item = nx.relabel.convert_node_labels_to_integers(
                self.represent_data(item), relabel_label)
            if not (item.graph.get("kind") == "scalar" and not item.graph.get("style")):
                best_style = False
            data.append(item)
            relabel_label += item.number_of_nodes()
            node = nx.union(node, item)
        for d0, d1 in pairwise(data):
            self.add_data_edge(node, d0, d1)

        if flow_style is None:
            if self.default_flow_style is not None:
                node.flow_style = self.default_flow_style
            else:
                node.flow_style = best_style
        return node

    def represent_mapping(self, tag, mapping, flow_style=None):
        node = nx.MultiGraph(kind="mapping", tag=tag, flow_style=flow_style)
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        best_style = True
        if hasattr(mapping, 'items'):
            mapping = list(mapping.items())
            if self.sort_keys:
                try:
                    mapping = sorted(mapping)
                except TypeError:
                    pass
        relabel_label = 0
        for item_key, item_value in enumerate(mapping):
            item_key = nx.relabel.convert_node_labels_to_integers(
                self.represent_data(item_key), relabel_label)
            relabel_label += item_key.number_of_nodes()
            item_value = nx.relabel.convert_node_labels_to_integers(
                self.represent_data(item_value), relabel_label)
            relabel_label += item_value.number_of_nodes()
            if not (item_key.graph.get("kind") == "scalar" and not item_key.graph.get("style")):
                best_style = False
            if not (item_value.graph.get("kind") == "scalar" and not item_value.graph.get("style")):
                best_style = False
            node = nx.union_all([node, item_key, item_value])
            self.add_data_edge(node, item_key, item_value)
            relabel_label += 1
        if flow_style is None:
            if self.default_flow_style is not None:
                node.flow_style = self.default_flow_style
            else:
                node.flow_style = best_style
        return node

    def ignore_aliases(self, data):
        return False

    def add_data_edge(self, node, head, tail):
        edge_id = node.number_of_nodes()
        node.add_node(edge_id, bipartite=1)
        for n, b in head.nodes(data="bipartite"):
            if b == 0:
                node.add_edge(edge_id, n, direction="head")
        for n, b in tail.nodes(data="bipartite"):
            if b == 0:
                node.add_edge(edge_id, n, direction="tail")
        return node
