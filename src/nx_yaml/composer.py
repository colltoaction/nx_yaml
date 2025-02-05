
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

    def compose_stream(self):
        if not self.check_event(StreamStartEvent):
            raise ComposerError(None, None, f"expected StreamStartEvent not {self.event[0]}")

        # Compose the root node.
        stream_start_event = self.get_event()
        node = nx.DiGraph()
        node.add_node(0, bipartite=0, kind="stream")
        node.add_node(1, bipartite=1)
        node.add_edge(0, 1, event="start")

        while not self.check_event(StreamEndEvent):
            self.compose_document(node, 0, node.number_of_nodes())

        # # TODO many documents
        # # Ensure that the stream contains no more documents.
        # if not self.check_event(StreamEndEvent):
        #     raise ComposerError("expected a single document in the stream",
        #             None, "but found another document")

        stream_end_event = self.get_event()

        self.anchors = {}
        return node

    def compose_document(self, node, parent, index):
        if not self.check_event(DocumentStartEvent):
            raise ComposerError(None, None, f"expected DocumentStartEvent not {self.event[0]}")

        # Drop the DOCUMENT-START event.
        self.get_event()

        # Compose the root node.
        node.add_node(index, bipartite=0, kind="document")
        node.add_node(index+1, bipartite=1)
        node.add_edge(index, index+1)
        node.add_edge(parent+1, index, event="start")
        self.compose_node(node, index, index+2)

        if not self.check_event(DocumentEndEvent):
            raise ComposerError(None, None, f"expected DocumentEndEvent not {self.event[0]}")

        # Drop the DOCUMENT-END event.
        self.get_event()

        self.anchors = {}

    def compose_node(self, node, parent, index):
        if self.check_event(AliasEvent):
            self.compose_alias_node(node, parent, index)
        elif self.check_event(ScalarEvent):
            self.compose_scalar_node(node, parent, index)
        elif self.check_event(SequenceStartEvent):
            self.compose_sequence_node(node, parent, index)
        elif self.check_event(MappingStartEvent):
            self.compose_mapping_node(node, parent, index)
        else:
            raise ComposerError(None, None, f"unexpected event {self.event[0]}")

    def compose_alias_node(self, node, parent, index):
        event = self.get_event()
        anchor = event.anchor
        if anchor not in self.anchors:
            raise ComposerError(None, None, "found undefined alias %r"
                    % anchor, event.start_mark)
        # return self.anchors[anchor]
        node.add_node(index, bipartite=0,
                kind="alias", anchor=anchor)
        node.add_node(index+1, bipartite=1)
        node.add_edge(parent+1, index)
        node.add_edge(index, index+1, direction="tail")
        return node

    def compose_scalar_node(self, node, parent, index):
        event = self.get_event()
        tag = event.tag
        if tag is None or tag == '!':
            tag = self.resolve("scalar", event.value, event.implicit)
        anchor = event.anchor
        if anchor:
            self.anchors[anchor] = index
        node.add_node(index, bipartite=0,
                kind="scalar", tag=tag, value=event.value,
                start_mark=event.start_mark,
                end_mark=event.end_mark,
                flow_style=event.style)
        node.add_node(index+1, bipartite=1)
        node.add_edge(parent+1, index)
        node.add_edge(index, index+1, direction="tail")
        return node

    def compose_sequence_node(self, node, parent, index):
        start_event = self.get_event()
        tag = start_event.tag
        if tag is None or tag == '!':
            tag = self.resolve("sequence", None, start_event.implicit)
        node.add_node(index, bipartite=0,
                kind="sequence", tag=tag,
                start_mark=start_event.start_mark,
                flow_style=start_event.flow_style)
        node.add_node(index+1, bipartite=1)
        node.add_edge(index, index+1, direction="tail")
        node.add_edge(parent+1, index)
        while not self.check_event(SequenceEndEvent):
            k = node.number_of_nodes()
            self.compose_node(node, index, k)
        end_event = self.get_event()
        node.nodes[0]["end_mark"] = end_event.end_mark
        return node

    def compose_mapping_node(self, node, parent, index):
        start_event = self.get_event()
        tag = start_event.tag
        if tag is None or tag == '!':
            tag = self.resolve("mapping", None, start_event.implicit)
        node.add_node(index, bipartite=0,
                kind="mapping", tag=tag,
                start_mark=start_event.start_mark,
                flow_style=start_event.flow_style)
        node.add_node(index+1, bipartite=1)
        node.add_edge(index, index+1, direction="tail")
        node.add_edge(parent+1, index)

        while not self.check_event(MappingEndEvent):
            k = node.number_of_nodes()
            self.compose_node(node, index, k)
            v = node.number_of_nodes()
            self.compose_node(node, index, v)

        end_event = self.get_event()
        node.end_mark = end_event.end_mark
        node.nodes[0]["end_mark"] = end_event.end_mark
        return node

