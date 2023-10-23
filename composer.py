
__all__ = ['NxComposer']

from yaml import AliasEvent, MappingEndEvent, MappingStartEvent, ScalarEvent, SequenceEndEvent, SequenceStartEvent, StreamStartEvent, StreamEndEvent
from yaml.composer import ComposerError
import networkx as nx

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
        document = nx.DiGraph()
        if not self.check_event(StreamEndEvent):
            document = self.compose_document()

        # Ensure that the stream contains no more documents.
        if not self.check_event(StreamEndEvent):
            event = self.get_event()
            document_start_mark = freeze_mark(document.graph["start_mark"]) if "start_mark" in document.graph else None
            raise ComposerError("expected a single document in the stream",
                    document_start_mark, "but found another document",
                    freeze_mark(event.start_mark))

        # Drop the STREAM-END event.
        self.get_event()

        return document

    def compose_document(self):
        # Drop the DOCUMENT-START event.
        self.get_event()

        # Compose the root node.
        node = nx.DiGraph()

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

    def compose_scalar_node(self, anchor):
        event = self.get_event()
        tag = event.tag
        if tag is None or tag == '!':
            tag = self.resolve("scalar", event.value, event.implicit)
        node = nx.DiGraph(kind='scalar', tag=tag, value=event.value,
                start_mark=freeze_mark(event.start_mark), end_mark=freeze_mark(event.end_mark), style=event.style)
        if anchor is not None:
            self.anchors[anchor] = node
        return node

    def compose_sequence_node(self, anchor):
        start_event = self.get_event()
        tag = start_event.tag
        if tag is None or tag == '!':
            tag = self.resolve("sequence", None, start_event.implicit)
        node = nx.DiGraph(kind='sequence')
        node.add_node((),
                kind='sequence', tag=tag,
                start_event=freeze_mark(start_event.start_mark),
                flow_style=start_event.flow_style)
        if anchor is not None:
            self.anchors[anchor] = node
        index = 0
        while not self.check_event(SequenceEndEvent):
            node.value.append(self.compose_node(node, index))
            index += 1
        end_event = self.get_event()
        node.end_mark = freeze_mark(end_event.end_mark)
        return node

    def compose_mapping_node(self, anchor):
        assert print("mapping")
        start_event = self.get_event()
        tag = start_event.tag
        if tag is None or tag == '!':
            tag = self.resolve("mapping", None, start_event.implicit)
        node = nx.DiGraph(kind='mapping')
        node.add_node((),
                kind='mapping', tag=tag,
                start_mark=freeze_mark(start_event.start_mark),
                flow_style=start_event.flow_style)
        if anchor is not None:
            self.anchors[anchor] = node
        while not self.check_event(MappingEndEvent):
            #key_event = self.peek_event()
            item_key = self.compose_node(node, None)
            #if item_key in node.value:
            #    raise ComposerError("while composing a mapping", freeze_mark(start_event.start_mark),
            #            "found duplicate key", freeze_mark(key_event.start_mark))
            item_value = self.compose_node(node, item_key)
            #node.value[item_key] = item_value
            node.value.append((item_key, item_value))
        end_event = self.get_event()
        node.end_mark = freeze_mark(end_event.end_mark)
        return node

def freeze_mark(self):
    return {
        "name": self.name,
        "index": self.index,
        "line": self.line,
        "column": self.column,
        "buffer": self.buffer,
        "pointer": self.pointer,
    }
