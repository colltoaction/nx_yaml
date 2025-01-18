
__all__ = ['NxComposer', 'ComposerError']

import networkx as nx
from yaml.error import MarkedYAMLError
from yaml.events import *

from .nodes import mapping_append, sequence_append

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
        stream_start_event = self.get_event()

        # Compose a document if the stream is not empty.
        document = nx.DiGraph()
        if not self.check_event(StreamEndEvent):
            document = self.compose_document()

        # Ensure that the stream contains no more documents.
        if not self.check_event(StreamEndEvent):
            event = self.get_event()
            raise ComposerError("expected a single document in the stream",
                    document.start_mark, "but found another document",
                    event.start_mark)

        stream_end_event = self.get_event()
        document.graph["stream_start_event"] = stream_start_event
        document.graph["stream_end_event"] = stream_end_event

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
        node = nx.DiGraph()
        node.add_node(0, bipartite=0,
                kind="scalar", tag=tag, value=event.value,
                start_mark=event.start_mark,
                end_mark=event.end_mark,
                flow_style=event.style)
        node.add_node(1, bipartite=1)
        node.add_edge(1, 0, direction="tail")
        if anchor is not None:
            self.anchors[anchor] = node
        return node

    def compose_sequence_node(self, anchor):
        start_event = self.get_event()
        tag = start_event.tag
        if tag is None or tag == '!':
            tag = self.resolve("sequence", None, start_event.implicit)
        node = nx.DiGraph()
        node.add_node(0, bipartite=0,
                kind="sequence", tag=tag,
                start_mark=start_event.start_mark,
                flow_style=start_event.flow_style)
        node.add_node(1, bipartite=1)
        node.add_edge(1, 0, direction="tail")
        if anchor is not None:
            self.anchors[anchor] = node
        index = 0
        while not self.check_event(SequenceEndEvent):
            node_at_index = self.compose_node(node, index)
            sequence_append(node, node_at_index)
            index += 1
        end_event = self.get_event()
        node.nodes[0]["end_mark"] = end_event.end_mark
        return node

    def compose_mapping_node(self, anchor):
        start_event = self.get_event()
        tag = start_event.tag
        if tag is None or tag == '!':
            tag = self.resolve("mapping", None, start_event.implicit)
        node = nx.DiGraph()
        node.add_node(0, bipartite=0,
                kind="mapping", tag=tag,
                start_mark=start_event.start_mark,
                flow_style=start_event.flow_style)
        self.prev_label = 0
        node.add_node(1, bipartite=1)
        node.add_edge(1, 0, direction="tail")

        if anchor is not None:
            self.anchors[anchor] = node
        while not self.check_event(MappingEndEvent):
            #key_event = self.peek_event()
            item_key = self.compose_node(node, None)
            #if item_key in node.value:
            #    raise ComposerError("while composing a mapping", start_event.start_mark,
            #            "found duplicate key", key_event.start_mark)
            item_value = self.compose_node(node, item_key)
            #node.value[item_key] = item_value
            node = mapping_append(node, item_key, item_value)

        end_event = self.get_event()
        node.end_mark = end_event.end_mark
        node.nodes[0]["end_mark"] = end_event.end_mark
        return node

