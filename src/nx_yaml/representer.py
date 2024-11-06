
__all__ = ['BaseRepresenter', 'NxSafeRepresenter',
    'RepresenterError']

from itertools import pairwise
import networkx as nx
from yaml.error import *

import datetime, copyreg, types, base64, collections

from .nodes import add_data_edge

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
        node.add_node(0, bipartite=1, kind="scalar", tag=tag, style=style)
        if value:
            node.add_node(1, bipartite=0, value=value)
            node.add_edge(0, 1, direction="head")
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        return node

    def represent_sequence(self, tag, sequence, flow_style=None):
        node = nx.MultiGraph(kind="sequence")
        node.add_node(0, bipartite=1, kind="sequence", tag=tag, flow_style=flow_style)
        relabel_label = 1
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        best_style = True
        data = []
        for item in sequence:
            item = self.represent_data(item)
            item = nx.relabel.convert_node_labels_to_integers(item, relabel_label)
            scalars = item[relabel_label]
            if not (item.graph.get("kind") == "scalar" and not item.graph.get("style")):
                best_style = False
            data.append(relabel_label)
            relabel_label += item.number_of_nodes()
            node = nx.union(node, item)
            # TODO each item is linked from the root
            # as well as pairwise
        for d0, d1 in pairwise([0] + data):
            add_data_edge(node, d0, d1)
            node.add_edge(d0, d1, direction="head")

        if flow_style is None:
            if self.default_flow_style is not None:
                node.flow_style = self.default_flow_style
            else:
                node.flow_style = best_style
        return node

    def represent_mapping(self, tag, mapping, flow_style=None):
        node = nx.MultiGraph(kind="mapping")
        node.add_node(0, bipartite=1, kind="mapping", tag=tag, flow_style=flow_style)
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
            root_key = relabel_label
            item_key = self.represent_data(item_key)
            item_key = nx.relabel.convert_node_labels_to_integers(item_key, root_key)
            relabel_label += item_key.number_of_nodes()
            value_key = relabel_label
            item_value = self.represent_data(item_value)
            item_value = nx.relabel.convert_node_labels_to_integers(item_value, value_key)
            relabel_label += item_value.number_of_nodes()
            if not (item_key.graph.get("kind") == "scalar" and not item_key.graph.get("style")):
                best_style = False
            if not (item_value.graph.get("kind") == "scalar" and not item_value.graph.get("style")):
                best_style = False
            node = nx.union_all([node, item_key, item_value])
            edge_key = relabel_label
            node.add_node(edge_key, bipartite=1)
            relabel_label += 1
            for s in node[root_key]:
                node.add_edge(0, s, direction="head")
                node.add_edge(edge_key, s, direction="head")
            for s in node[value_key]:
                node.add_edge(edge_key, s, direction="tail")
        if flow_style is None:
            if self.default_flow_style is not None:
                node.flow_style = self.default_flow_style
            else:
                node.flow_style = best_style
        return node

    def ignore_aliases(self, data):
        return False
