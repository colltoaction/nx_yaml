
__all__ = ['NxComposer']

import itertools
from yaml import AliasEvent, MappingEndEvent, MappingStartEvent, ScalarEvent, SequenceEndEvent, SequenceStartEvent, StreamStartEvent, StreamEndEvent
from yaml.composer import ComposerError
import networkx as nx

class NxComposer:
    """
    Produce an nx.DiGraph from a YAML event stream.
    The result is a nested structure of digraphs
    where the kind attribute indicates the substructure.
    To obtain a flat nx.DiGraph we merge and add an edge between
    the roots of each linked digraph.
    """

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
        document = nx.DiGraph()
        if not self.check_event(StreamEndEvent):
            document = self.compose_document()

        # Ensure that the stream contains no more documents.
        if not self.check_event(StreamEndEvent):
            event = self.get_event()
            document_start_mark = freeze_mark(document.graph["start_mark"]) if "start_mark" in document.graph else None
            event_start_mark = freeze_mark(event.start_mark)
            raise ComposerError("expected a single document in the stream",
                    document_start_mark, "but found another document",
                    event_start_mark)

        # Drop the STREAM-END event.
        self.get_event()

        return document

    def compose_document(self) -> nx.DiGraph:
        # Drop the DOCUMENT-START event.
        self.get_event()

        # Compose the root node.
        node = self.compose_node(nx.DiGraph(), None)

        # Drop the DOCUMENT-END event.
        self.get_event()

        self.anchors = {}
        return node

    def compose_node(self, parent, index) -> nx.DiGraph:
        if self.check_event(AliasEvent):
            event = self.get_event()
            anchor = event.anchor
            if anchor not in self.anchors:
                raise ComposerError(None, None, "found undefined alias %r"
                        % anchor, freeze_mark(event.start_mark))
            return self.anchors[anchor]
        event = self.peek_event()
        anchor = event.anchor
        if anchor is not None:
            if anchor in self.anchors:
                raise ComposerError("found duplicate anchor %r; first occurrence"
                        % anchor, freeze_mark(self.anchors[anchor].start_mark),
                        "second occurrence", freeze_mark(event.start_mark))
        self.descend_resolver(parent, index)
        if self.check_event(ScalarEvent):
            node = self.compose_scalar_node(anchor)
        elif self.check_event(SequenceStartEvent):
            node = self.compose_sequence_node(anchor)
        elif self.check_event(MappingStartEvent):
            node = self.compose_mapping_node(anchor)
        self.ascend_resolver()
        return node

    def compose_scalar_node(self, anchor) -> nx.DiGraph:
        event = self.get_event()
        tag = event.tag
        if tag is None or tag == '!':
            tag = self.resolve("scalar", event.value, event.implicit)
        node = nx.DiGraph(kind='scalar', tag=tag, value=event.value,
                start_mark=freeze_mark(event.start_mark), end_mark=freeze_mark(event.end_mark), style=event.style)
        node.add_node(event.value)
        if anchor is not None:
            self.anchors[anchor] = node
        return node

    def compose_sequence_node(self, anchor) -> nx.DiGraph:
        start_event = self.get_event()
        tag = start_event.tag
        if tag is None or tag == '!':
            tag = self.resolve("sequence", None, start_event.implicit)
        node = nx.DiGraph(kind='sequence', tag=tag,
                    start_event=freeze_mark(start_event.start_mark),
                    flow_style=start_event.flow_style)
        if anchor is not None:
            self.anchors[anchor] = node
        index = 0
        child_nodes = []
        while not self.check_event(SequenceEndEvent):
            child_node = self.compose_node(node, index)
            child_nodes.append(child_node)
            node.update(edges=child_node.edges, nodes=child_node.nodes)
        child_nodes = [list(nx.algorithms.topological_sort(n)) for n in child_nodes]
        edges = itertools.pairwise(child_nodes)
        for src, tgt in edges:
            print(node.nodes, node.edges)
            first_src = src[0]
            first_tgt = tgt[0]
            node.add_edge(first_src, first_tgt)
            index += 1

        # edges = itertools.combinations(child_nodes, 2)
        # node.add_edges_from(edges)
        end_event = self.get_event()
        node.graph["end_mark"] = freeze_mark(end_event.end_mark)
        return node

    def compose_mapping_node(self, anchor) -> nx.DiGraph:
        start_event = self.get_event()
        tag = start_event.tag
        if tag is None or tag == '!':
            tag = self.resolve("mapping", None, start_event.implicit)
        node = nx.DiGraph(kind='mapping')
        if anchor is not None:
            self.anchors[anchor] = node
        while not self.check_event(MappingEndEvent):
            item_key = self.compose_node(node, None)
            item_value = self.compose_node(node, item_key)
            node.update(nodes=item_key.nodes, edges=item_key.edges)
            node.update(nodes=item_value.nodes, edges=item_value.edges)
            node.add_edges_from(
                itertools.product(
                    (n for n, d in item_key.in_degree() if d == 0),
                    (n for n, d in item_value.in_degree() if d == 0)))
        end_event = self.get_event()
        node.end_mark = freeze_mark(end_event.end_mark)
        return node

def freeze_mark(mark):
    return {
        "name": mark.name,
        "index": mark.index,
        "line": mark.line,
        "column": mark.column,
        "buffer": mark.buffer,
        "pointer": mark.pointer,
    }
