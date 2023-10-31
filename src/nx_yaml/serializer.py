
__all__ = ['NxSerializer']

from yaml.serializer import SerializerError
from yaml import AliasEvent, DocumentEndEvent, DocumentStartEvent, MappingEndEvent, MappingStartEvent, ScalarEvent, SequenceEndEvent, SequenceStartEvent, StreamStartEvent, StreamEndEvent
import networkx as nx

class NxSerializer:

    ANCHOR_TEMPLATE = 'id%03d'

    def __init__(self, encoding=None,
            explicit_start=None, explicit_end=None, version=None, tags=None):
        self.use_encoding = encoding
        self.use_explicit_start = explicit_start
        self.use_explicit_end = explicit_end
        self.use_version = version
        self.use_tags = tags
        self.serialized_nodes = {}
        self.anchors = {}
        self.last_anchor_id = 0
        self.closed = None

    def open(self):
        if self.closed is None:
            self.emit(StreamStartEvent(encoding=self.use_encoding))
            self.closed = False
        elif self.closed:
            raise SerializerError("serializer is closed")
        else:
            raise SerializerError("serializer is already opened")

    def close(self):
        if self.closed is None:
            raise SerializerError("serializer is not opened")
        elif not self.closed:
            self.emit(StreamEndEvent())
            self.closed = True

    #def __del__(self):
    #    self.close()

    def serialize(self, node):
        if self.closed is None:
            raise SerializerError("serializer is not opened")
        elif self.closed:
            raise SerializerError("serializer is closed")
        self.emit(DocumentStartEvent(explicit=self.use_explicit_start,
            version=self.use_version, tags=self.use_tags))
        self.anchor_node(node)
        self.serialize_node(node, None, None)
        self.emit(DocumentEndEvent(explicit=self.use_explicit_end))
        self.serialized_nodes = {}
        self.anchors = {}
        self.last_anchor_id = 0

    def anchor_node(self, node: nx.DiGraph):
        if node in self.anchors:
            if self.anchors[node] is None:
                self.anchors[node] = self.generate_anchor(node)
        else:
            self.anchors[node] = None
            kind = node.graph["kind"] if "kind" in node.graph else "scalar"
            if kind == "sequence":
                for item in node.value:
                    self.anchor_node(item)
            elif kind == "mapping":
                for key, value in node.value:
                    self.anchor_node(key)
                    self.anchor_node(value)

    def generate_anchor(self, node):
        self.last_anchor_id += 1
        return self.ANCHOR_TEMPLATE % self.last_anchor_id

    def serialize_node(self, node, parent, index):
        alias = self.anchors[node]
        if node in self.serialized_nodes:
            self.emit(AliasEvent(alias))
        else:
            self.serialized_nodes[node] = True
            self.descend_resolver(parent, index)
            kind = node.graph["kind"] if "kind" in node.graph else "scalar"
            tag = node.graph["tag"] if "tag" in node.graph else "tag:yaml.org,2002:str"
            if kind == "scalar":
                value = node.graph["value"] if "value" in node.graph else ""
                style = node.graph["style"] if "style" in node.graph else None
                detected_tag = self.resolve("scalar", value, (True, False))
                default_tag = self.resolve("scalar", value, (False, True))
                implicit = (tag == detected_tag), (tag == default_tag)
                self.emit(ScalarEvent(alias, tag, implicit, value,
                    style=style))
            elif kind == "sequence":
                value = node.graph["value"]
                implicit = (tag
                            == self.resolve("sequence", value, True))
                self.emit(SequenceStartEvent(alias, tag, implicit,
                    flow_style=node.flow_style))
                index = 0
                for item in value:
                    self.serialize_node(item, node, index)
                    index += 1
                self.emit(SequenceEndEvent())
            elif kind == "mapping":
                value = node.graph["value"]
                implicit = (tag
                            == self.resolve("mapping", value, True))
                self.emit(MappingStartEvent(alias, tag, implicit,
                    flow_style=node.flow_style))
                for key, value in value:
                    self.serialize_node(key, node, None)
                    self.serialize_node(value, node, key)
                self.emit(MappingEndEvent())
            self.ascend_resolver()

