
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
        (_, start_mark, end_mark, anchor) = event
        (start_mark_name, start_mark_index, start_mark_line, start_mark_column, start_mark_buffer, start_mark_pointer) = (start_mark.name, start_mark.index, start_mark.line, start_mark.column, start_mark.buffer, start_mark.pointer)
        (end_mark_name, end_mark_index, end_mark_line, end_mark_column, end_mark_buffer, end_mark_pointer) = (end_mark.name, end_mark.index, end_mark.line, end_mark.column, end_mark.buffer, end_mark.pointer)
        node.add_node(index,
                bipartite=0,
                start_mark_name=start_mark_name or "", start_mark_index=start_mark_index or "", start_mark_line=start_mark_line or "", start_mark_column=start_mark_column or "", start_mark_buffer=start_mark_buffer or "", start_mark_pointer=start_mark_pointer or "",
                end_mark_name=end_mark_name or "", end_mark_index=end_mark_index or "", end_mark_line=end_mark_line or "", end_mark_column=end_mark_column or "", end_mark_buffer=end_mark_buffer or "", end_mark_pointer=end_mark_pointer or "",
                kind="alias", anchor=anchor or "")
        node.add_node(index+1, bipartite=1)
        node.add_edge(parent+1, index)
        node.add_edge(index, index+1, direction="tail")
        return node

    def compose_scalar_node(self, node, parent, index):
        if not self.peek_event()[0] == "ScalarEvent":
            raise ComposerError(None, None, f"unexpected event {self.peek_event()[0]}")
        event = self.get_event()
        (_, start_mark, end_mark, anchor, tag, implicit, value, style) = event
        (start_mark_name, start_mark_index, start_mark_line, start_mark_column, start_mark_buffer, start_mark_pointer) = (start_mark.name, start_mark.index, start_mark.line, start_mark.column, start_mark.buffer, start_mark.pointer)
        (end_mark_name, end_mark_index, end_mark_line, end_mark_column, end_mark_buffer, end_mark_pointer) = (end_mark.name, end_mark.index, end_mark.line, end_mark.column, end_mark.buffer, end_mark.pointer)
        node.add_node(index,
                bipartite=0,
                implicit=implicit or "",
                start_mark_name=start_mark_name or "", start_mark_index=start_mark_index or "", start_mark_line=start_mark_line or "", start_mark_column=start_mark_column or "", start_mark_buffer=start_mark_buffer or "", start_mark_pointer=start_mark_pointer or "",
                end_mark_name=end_mark_name or "", end_mark_index=end_mark_index or "", end_mark_line=end_mark_line or "", end_mark_column=end_mark_column or "", end_mark_buffer=end_mark_buffer or "", end_mark_pointer=end_mark_pointer or "",
                style=style or "",
                kind="scalar", tag=tag or "", value=value or "", anchor=anchor or "")
        node.add_node(index+1, bipartite=1)
        node.add_edge(parent+1, index)
        node.add_edge(index, index+1, direction="tail")
        return node

    def compose_sequence_node(self, node, parent, index):
        if not self.peek_event()[0] == "SequenceStartEvent":
            raise ComposerError(None, None, f"unexpected event {self.peek_event()[0]}")
        start_event = self.get_event()
        (_, start_mark, end_mark, anchor, tag, implicit, flow_style) = start_event
        (start_mark_name, start_mark_index, start_mark_line, start_mark_column, start_mark_buffer, start_mark_pointer) = (start_mark.name, start_mark.index, start_mark.line, start_mark.column, start_mark.buffer, start_mark.pointer)
        (end_mark_name, end_mark_index, end_mark_line, end_mark_column, end_mark_buffer, end_mark_pointer) = (end_mark.name, end_mark.index, end_mark.line, end_mark.column, end_mark.buffer, end_mark.pointer)
        node.add_node(index,
                bipartite=0,
                implicit=implicit or "",
                start_mark_name=start_mark_name or "", start_mark_index=start_mark_index or "", start_mark_line=start_mark_line or "", start_mark_column=start_mark_column or "", start_mark_buffer=start_mark_buffer or "", start_mark_pointer=start_mark_pointer or "",
                end_mark_name=end_mark_name or "", end_mark_index=end_mark_index or "", end_mark_line=end_mark_line or "", end_mark_column=end_mark_column or "", end_mark_buffer=end_mark_buffer or "", end_mark_pointer=end_mark_pointer or "",
                flow_style=flow_style or "",
                kind="sequence", tag=tag or "", anchor=anchor or "")
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
        (_, start_mark, end_mark, anchor, tag, implicit, flow_style) = start_event
        (start_mark_name, start_mark_index, start_mark_line, start_mark_column, start_mark_buffer, start_mark_pointer) = (start_mark.name, start_mark.index, start_mark.line, start_mark.column, start_mark.buffer, start_mark.pointer)
        (end_mark_name, end_mark_index, end_mark_line, end_mark_column, end_mark_buffer, end_mark_pointer) = (end_mark.name, end_mark.index, end_mark.line, end_mark.column, end_mark.buffer, end_mark.pointer)
        node.add_node(index,
                bipartite=0,
                implicit=implicit or "",
                start_mark_name=start_mark_name or "", start_mark_index=start_mark_index or "", start_mark_line=start_mark_line or "", start_mark_column=start_mark_column or "", start_mark_buffer=start_mark_buffer or "", start_mark_pointer=start_mark_pointer or "",
                end_mark_name=end_mark_name or "", end_mark_index=end_mark_index or "", end_mark_line=end_mark_line or "", end_mark_column=end_mark_column or "", end_mark_buffer=end_mark_buffer or "", end_mark_pointer=end_mark_pointer or "",
                flow_style=flow_style or "",
                kind="mapping", tag=tag or "", anchor=anchor or "")
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

