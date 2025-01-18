
__all__ = ['NxSerializer', 'SerializerError']

import networkx as nx
from yaml.error import Mark
from yaml.serializer import SerializerError
from yaml.events import *

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
            self.emit(StreamStartEvent(
                start_mark=None,
                end_mark=None,
                encoding=self.use_encoding))
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
        self.emit(DocumentStartEvent(
            start_mark=Mark(
                node.graph.get("document_end_start_mark_name"),
                node.graph.get("document_end_start_mark_index"),
                node.graph.get("document_end_start_mark_line"),
                node.graph.get("document_end_start_mark_column"),
                node.graph.get("document_end_start_mark_buffer"),
                node.graph.get("document_end_start_mark_pointer")),
            end_mark=Mark(
                node.graph.get("document_end_end_mark_name"),
                node.graph.get("document_end_end_mark_index"),
                node.graph.get("document_end_end_mark_line"),
                node.graph.get("document_end_end_mark_column"),
                node.graph.get("document_end_end_mark_buffer"),
                node.graph.get("document_end_end_mark_pointer")),
            explicit=node.graph.get("document_start_use_explicit_start"),
            version=node.graph.get("document_start_use_version"),
            tags=node.graph.get("document_start_use_tags")))
        self.anchor_node(node)
        self.serialize_node(node, None, 0)
        self.emit(DocumentEndEvent(
            start_mark=Mark(
                node.graph.get("document_end_start_mark_name"),
                node.graph.get("document_end_start_mark_index"),
                node.graph.get("document_end_start_mark_line"),
                node.graph.get("document_end_start_mark_column"),
                node.graph.get("document_end_start_mark_buffer"),
                node.graph.get("document_end_start_mark_pointer")),
            end_mark=Mark(
                node.graph.get("document_end_end_mark_name"),
                node.graph.get("document_end_end_mark_index"),
                node.graph.get("document_end_end_mark_line"),
                node.graph.get("document_end_end_mark_column"),
                node.graph.get("document_end_end_mark_buffer"),
                node.graph.get("document_end_end_mark_pointer")),
            explicit=node.graph.get("document_end_explicit")))
        self.serialized_nodes = {}
        self.anchors = {}
        self.last_anchor_id = 0

    def anchor_node(self, node: nx.DiGraph):
        return
        if node in self.anchors:
            if self.anchors[node] is None:
                self.anchors[node] = self.generate_anchor(node)
        else:
            self.anchors[node] = None
            if node.nodes[index].get("kind") == "sequence":
                # TODO iterate according to representer
                for item in node:
                    self.anchor_node(item)
            elif node.nodes[index].get("kind") == "mapping":
                # TODO iterate according to representer
                for key, value in node:
                    self.anchor_node(key)
                    self.anchor_node(value)

    def generate_anchor(self, node):
        self.last_anchor_id += 1
        return self.ANCHOR_TEMPLATE % self.last_anchor_id

    def serialize_node(self, node, parent, index):
        # alias = self.anchors[node]
        if node in self.serialized_nodes:
            self.emit(AliasEvent(node.nodes[index].get("anchor")))
        else:
            # print(node.graph)
            # print(node.nodes(data=True))
            # self.serialized_nodes[node] = True
            self.descend_resolver(parent, index)
            if not node:
                pass
            elif node.nodes[index].get("kind") == "scalar":
                # TODO
                detected_tag = self.resolve("scalar", node, (True, False))
                default_tag = self.resolve("scalar", node, (False, True))
                implicit = True, True

                self.emit(ScalarEvent(
                    node.nodes[index].get("anchor"),
                    node.nodes[index].get("tag"),
                    implicit,
                    node.nodes[index].get("value"),
                    start_mark=Mark(
                        node.nodes[index].get("start_mark_name"),
                        node.nodes[index].get("start_mark_index"),
                        node.nodes[index].get("start_mark_line"),
                        node.nodes[index].get("start_mark_column"),
                        node.nodes[index].get("start_mark_buffer"),
                        node.nodes[index].get("start_mark_pointer")),
                    end_mark=Mark(
                        node.nodes[index].get("end_mark_name"),
                        node.nodes[index].get("end_mark_index"),
                        node.nodes[index].get("end_mark_line"),
                        node.nodes[index].get("end_mark_column"),
                        node.nodes[index].get("end_mark_buffer"),
                        node.nodes[index].get("end_mark_pointer")),
                    style=node.nodes[index].get("style")))
            elif node.nodes[index].get("kind") == "sequence":
                implicit = (node.nodes[index].get("tag")
                # TODO iterate according to representer
                            == self.resolve("sequence", node, True))
                self.emit(SequenceStartEvent(node.nodes[index].get("anchor"), node.nodes[index].get("tag"), implicit,
                    flow_style=node.nodes[index].get("flow_style")))
                index = 0
                # TODO iterate according to representer
                for item in node:
                    self.serialize_node(item, node, index)
                    index += 1
                self.emit(SequenceEndEvent())
            elif node.nodes[index].get("kind") == "mapping":
                implicit = (node.nodes[index].get("tag")
                # TODO iterate according to representer
                            == self.resolve("mapping", node, True))
                self.emit(MappingStartEvent(
                    node.nodes[index].get("anchor"),
                    node.nodes[index].get("tag"),
                    implicit,
                    flow_style=node.nodes[index].get("flow_style")))
                    # TODO iterate according to representer
                for e in node[index + 1]:
                    if e != index:
                        self.serialize_node(node, index, e)
                self.emit(MappingEndEvent())
            self.ascend_resolver()

