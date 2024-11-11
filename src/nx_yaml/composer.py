
__all__ = ['NxComposer', 'ComposerError']

from itertools import pairwise, product
import networkx as nx
from yaml.error import MarkedYAMLError
from yaml.events import *


class ComposerError(MarkedYAMLError):
    pass

class NxComposer:

    def __init__(self):
        self.anchors = {}

    def check_node(self):
        # Drop the STREAM-START event.
        if self.check_event(StreamStartEvent):
            self.get_event()

        # If there are more documents available?
        return not self.check_event(StreamEndEvent)

    def get_node(self):
        # Get the root node of the next document.
        if not self.check_event(StreamEndEvent):
            return self.compose_document()

    def get_single_node(self):
        # Drop the STREAM-START event.
        self.get_event()

        # Compose a document if the stream is not empty.
        document = None
        if not self.check_event(StreamEndEvent):
            document = self.compose_document()

        # Ensure that the stream contains no more documents.
        if not self.check_event(StreamEndEvent):
            event = self.get_event()
            raise ComposerError("expected a single document in the stream",
                    document.start_mark, "but found another document",
                    event.start_mark)

        # Drop the STREAM-END event.
        self.get_event()

        return document

    def compose_document(self):
        # Drop the DOCUMENT-START event.
        self.get_event()

        # Compose the root node.
        node = self.compose_node(None, None)

        # Drop the DOCUMENT-END event.
        self.get_event()

        self.anchors = {}
        return node

    def compose_node(self, parent, index):
        if self.check_event(AliasEvent):
            event = self.get_event()
            anchor = event.anchor
            if anchor not in self.anchors:
                raise ComposerError(None, None, "found undefined alias %r"
                        % anchor, event.start_mark)
            return self.anchors[anchor]
        event = self.peek_event()
        anchor = event.anchor
        if anchor is not None:
            if anchor in self.anchors:
                raise ComposerError("found duplicate anchor %r; first occurrence"
                        % anchor, self.anchors[anchor].start_mark,
                        "second occurrence", event.start_mark)
        self.descend_resolver(parent, index)
        if self.check_event(ScalarEvent):
            node = self.compose_scalar_node(anchor)
        elif self.check_event(SequenceStartEvent):
            node = self.compose_sequence_node(anchor)
        elif self.check_event(MappingStartEvent):
            node = self.compose_mapping_node(anchor)
        self.ascend_resolver()
        return node

    def compose_scalar_node(self, anchor):
        event = self.get_event()
        tag = event.tag
        if tag is None or tag == '!':
            tag = self.resolve("scalar", event.value, event.implicit)

        node = nx.MultiGraph(kind="scalar")
        node.add_node(0, bipartite=1, kind="scalar", tag=tag, value=event.value,
                start_mark=event.start_mark,
                end_mark=event.end_mark,
                flow_style=event.style)
        if event.value:
            node.add_node(1, bipartite=0, value=event.value)
            node.add_edge(0, 1, direction="head")
        if anchor is not None:
            self.anchors[anchor] = node
        return node

    def compose_sequence_node(self, anchor):
        start_event = self.get_event()
        tag = start_event.tag
        if tag is None or tag == '!':
            tag = self.resolve("sequence", None, start_event.implicit)
    
        node = nx.MultiGraph(kind="sequence")
        node.add_node(0, bipartite=1, kind="sequence", tag=tag,
                start_mark=start_event.start_mark,
                end_mark=None,
                flow_style=start_event.flow_style)
        if anchor is not None:
            self.anchors[anchor] = node
        index = 0
        relabel_label = 1
        item_labels = []
        while not self.check_event(SequenceEndEvent):
            index += 1
            item_label = relabel_label
            item_labels.append(item_label)
            item = nx.relabel.convert_node_labels_to_integers(
                self.compose_node(node, index), item_label)
            relabel_label += item.number_of_nodes()
            node = nx.union(node, item)
        for u, v in pairwise(item_labels):
            for u2, v2 in product(node[u], node[v]):
                node.add_edge(u, u2, direction="head")
                node.add_edge(u, v2, direction="tail")
        end_event = self.get_event()
        node.end_mark = end_event.end_mark
        return node

    def compose_mapping_node(self, anchor):
        start_event = self.get_event()
        tag = start_event.tag
        if tag is None or tag == '!':
            tag = self.resolve("mapping", None, start_event.implicit)
        node = nx.MultiGraph(kind="mapping")
        node.add_node(0, bipartite=1, kind="mapping", tag=tag,
                start_mark=start_event.start_mark,
                end_mark=None,
                flow_style=start_event.flow_style)
        if anchor is not None:
            self.anchors[anchor] = node
        relabel_label = 1
        while not self.check_event(MappingEndEvent):
            #key_event = self.peek_event()
            root_key = relabel_label
            item_key = nx.relabel.convert_node_labels_to_integers(
                self.compose_node(node, None), root_key)
            relabel_label += item_key.number_of_nodes()
            value_key = relabel_label
            item_value = nx.relabel.convert_node_labels_to_integers(
                self.compose_node(node, item_key), value_key)
            relabel_label += item_value.number_of_nodes()
            #if item_key in node.value:
            #    raise ComposerError("while composing a mapping", start_event.start_mark,
            #            "found duplicate key", key_event.start_mark)
            #node.value[item_key] = item_value
            node = nx.union_all([node, item_key, item_value])
            for u in node[root_key]:
                node.add_edge(0, u, direction="head")
            for u, v in product(node[root_key], node[value_key]):
                node.add_edge(root_key, u, direction="head")
                node.add_edge(root_key, v, direction="tail")
        end_event = self.get_event()
        node.end_mark = end_event.end_mark
        return node

