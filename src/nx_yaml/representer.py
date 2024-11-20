
__all__ = ['BaseRepresenter', 'NxSafeRepresenter',
    'RepresenterError']

from itertools import pairwise, product
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
        if data_types[0] in (dict, frozenset):
            node = self.represent_mapping('tag:yaml.org,2002:map', data)
        elif data_types[0] in (list, tuple):
            node = self.represent_sequence('tag:yaml.org,2002:seq', data)
        elif data is None:
            node = self.represent_scalar('tag:yaml.org,2002:str', None)
        else:
            node = self.represent_scalar('tag:yaml.org,2002:str', str(data))
                    
        #if alias_key is not None:
        #    self.represented_objects[alias_key] = node
        return node

    def represent_scalar(self, tag, value, style=None):
        if style is None:
            style = self.default_style
        node = nx.MultiGraph(kind="scalar")
        node.add_node(0, bipartite=0, kind="scalar", tag=tag, value=value, style=style)
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        return node

    def represent_sequence(self, tag, sequence, flow_style=None):
        node = nx.MultiGraph(kind="sequence")
        node.add_node(0, bipartite=0, kind="sequence", tag=tag, flow_style=flow_style)
        relabel_label = 1
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        best_style = True
        prev_label = 0
        for item in sequence:
            item = self.represent_data(item)
            item_label = relabel_label
            item = nx.relabel.convert_node_labels_to_integers(item, item_label)
            if not (item.graph.get("kind") == "scalar" and not item.graph.get("style")):
                best_style = False
            node = nx.union(node, item)
            relabel_label += item.number_of_nodes()
            pair_label = relabel_label
            relabel_label += 1
            node.add_node(pair_label, bipartite=1)
            node.add_edge(pair_label, prev_label, direction="head")
            node.add_edge(pair_label, item_label, direction="tail")
            prev_label = item_label

        if flow_style is None:
            if self.default_flow_style is not None:
                node.flow_style = self.default_flow_style
            else:
                node.flow_style = best_style
        return node

    def represent_mapping(self, tag, mapping, flow_style=None):
        node = nx.MultiGraph(kind="mapping")
        node.add_node(0, bipartite=0, kind="mapping", tag=tag, flow_style=flow_style)
        relabel_label = 1
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
        for item_key, item_value in mapping:
            key_label = relabel_label
            item_key = self.represent_data(item_key)
            item_key = nx.relabel.convert_node_labels_to_integers(item_key, key_label)
            relabel_label += item_key.number_of_nodes()
            value_label = relabel_label
            item_value = self.represent_data(item_value)
            item_value = nx.relabel.convert_node_labels_to_integers(item_value, value_label)
            relabel_label += item_value.number_of_nodes()
            if not (item_key.graph.get("kind") == "scalar" and not item_key.graph.get("style")):
                best_style = False
            if not (item_value.graph.get("kind") == "scalar" and not item_value.graph.get("style")):
                best_style = False
            node = nx.union_all([node, item_key, item_value])
            pair_label = relabel_label
            relabel_label += 1
            node.add_node(pair_label, bipartite=1)
            node.add_edge(0, pair_label, direction="head")
            node.add_edge(pair_label, key_label, direction="head")
            node.add_edge(pair_label, value_label, direction="tail")
        if flow_style is None:
            if self.default_flow_style is not None:
                node.flow_style = self.default_flow_style
            else:
                node.flow_style = best_style
        return node

    def ignore_aliases(self, data):
        return False
