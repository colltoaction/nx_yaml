
__all__ = ['NxComposer']

import networkx as nx
from yaml.composer import ComposerError


class NxComposer:

    def __init__(self):
        self.anchors = {}

    def compose_stream(self):
        if not self.peek_event()[0] == "StreamStartEvent":
            raise ComposerError(None, None, f"expected StreamStartEvent not {self.peek_event()[0]}")

        # Compose the root node.
        stream_start_event = self.get_event()
        node = nx.DiGraph()
        node.add_node(0, bipartite=0, kind="stream")
        node.add_node(1, bipartite=1)
        node.add_edge(0, 1, event="start")

        while not self.peek_event()[0] == "StreamEndEvent":
            self.compose_document(node, 0, node.number_of_nodes())

        # # TODO many documents
        # # Ensure that the stream contains no more documents.
        # if self.peek_event()[0] == "StreamEndEvent":
        #     raise ComposerError("expected a single document in the stream",
        #             None, "but found another document")

        stream_end_event = self.get_event()

        self.anchors = {}
        return node

    def compose_document(self, node, parent, index):
        if not self.peek_event()[0] == "DocumentStartEvent":
            raise ComposerError(None, None, f"expected DocumentStartEvent not {self.peek_event()[0]}")

        # Drop the DOCUMENT-START event.
        self.get_event()

        # Compose the root node.
        node.add_node(index,
                bipartite=0, kind="document")
        node.add_node(index+1, bipartite=1)
        node.add_edge(index, index+1)
        node.add_edge(parent+1, index, event="start")
        self.compose_node(node, index, index+2)

        if not self.peek_event()[0] == "DocumentEndEvent":
            raise ComposerError(None, None, f"expected DocumentEndEvent not {self.peek_event()[0]}")

        # Drop the DOCUMENT-END event.
        self.get_event()

        self.anchors = {}

    def compose_node(self, node, parent, index):
        if self.peek_event()[0] == "AliasEvent":
            self.compose_alias_node(node, parent, index)
        elif self.peek_event()[0] == "ScalarEvent":
            self.compose_scalar_node(node, parent, index)
        elif self.peek_event()[0] == "SequenceStartEvent":
            self.compose_sequence_node(node, parent, index)
        elif self.peek_event()[0] == "MappingStartEvent":
            self.compose_mapping_node(node, parent, index)
        else:
            raise ComposerError(None, None, f"unexpected event {self.peek_event()[0]}")

    def compose_alias_node(self, node, parent, index):
        if not self.peek_event()[0] == "AliasEvent":
            raise ComposerError(None, None, f"unexpected event {self.peek_event()[0]}")
        event = self.get_event()
        (_, anchor, start_mark, end_mark) = event
        node.add_node(index,
                bipartite=0,
                start_mark=start_mark,
                end_mark=end_mark,
                kind="alias", anchor=anchor)
        node.add_node(index+1, bipartite=1)
        node.add_edge(parent+1, index)
        node.add_edge(index, index+1, direction="tail")
        return node

    def compose_scalar_node(self, node, parent, index):
        if not self.peek_event()[0] == "ScalarEvent":
            raise ComposerError(None, None, f"unexpected event {self.peek_event()[0]}")
        event = self.get_event()
        (_, anchor, tag, implicit, value, start_mark, end_mark, style) = event
        node.add_node(index,
                bipartite=0,
                implicit=implicit,
                start_mark=start_mark,
                end_mark=end_mark,
                style=style,
                kind="scalar", tag=tag, value=value, anchor=anchor)
        node.add_node(index+1, bipartite=1)
        node.add_edge(parent+1, index)
        node.add_edge(index, index+1, direction="tail")
        return node

    def compose_sequence_node(self, node, parent, index):
        if not self.peek_event()[0] == "SequenceStartEvent":
            raise ComposerError(None, None, f"unexpected event {self.peek_event()[0]}")
        start_event = self.get_event()
        (_, anchor, tag, implicit, start_mark, end_mark, flow_style) = start_event
        node.add_node(index,
                bipartite=0,
                implicit=implicit,
                start_mark=start_mark,
                end_mark=end_mark,
                flow_style=flow_style,
                kind="sequence", tag=tag, anchor=anchor)
        node.add_node(index+1, bipartite=1)
        node.add_edge(index, index+1, direction="tail")
        node.add_edge(parent+1, index)
        while not self.peek_event()[0] == "SequenceEndEvent":
            k = node.number_of_nodes()
            self.compose_node(node, index, k)
        end_event = self.get_event()
        return node

    def compose_mapping_node(self, node, parent, index):
        if not self.peek_event()[0] == "MappingStartEvent":
            raise ComposerError(None, None, f"unexpected event {self.peek_event()[0]}")
        start_event = self.get_event()
        (_, anchor, tag, implicit, start_mark, end_mark, flow_style) = start_event
        node.add_node(index,
                bipartite=0,
                implicit=implicit,
                start_mark=start_mark,
                end_mark=end_mark,
                flow_style=flow_style,
                kind="mapping", tag=tag, anchor=anchor)
        node.add_node(index+1, bipartite=1)
        node.add_edge(index, index+1, direction="tail")
        node.add_edge(parent+1, index)

        while not self.peek_event()[0] == "MappingEndEvent":
            k = node.number_of_nodes()
            self.compose_node(node, index, k)
            v = node.number_of_nodes()
            self.compose_node(node, index, v)

        end_event = self.get_event()
        return node

