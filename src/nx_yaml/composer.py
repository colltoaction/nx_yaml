
__all__ = ['NxComposer', 'ComposerError']

from itertools import combinations, pairwise, product
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
        else:
            document = nx.MultiGraph(**{"kind": "scalar", "network-type": "directed"})
            document.add_node(0, bipartite=1, kind="scalar", value="")

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

        node = nx.MultiGraph(**{"kind": "scalar", "network-type": "directed"})
        node.add_node(0, bipartite=0, kind="scalar", tag=tag, value=event.value,
                start_mark=event.start_mark,
                end_mark=event.end_mark,
                flow_style=event.style)
        # node.add_node(1, bipartite=1, value=event.value)
        # node.add_edge(0, 1, direction="tail")
        if anchor is not None:
            self.anchors[anchor] = node
        return node

    def compose_sequence_node(self, anchor):
        start_event = self.get_event()
        tag = start_event.tag
        if tag is None or tag == '!':
            tag = self.resolve("sequence", None, start_event.implicit)
    
        node = nx.MultiGraph(**{"kind": "sequence", "network-type": "directed"})
        node.add_node(0, bipartite=0, kind="sequence", tag=tag,
                start_mark=start_event.start_mark,
                end_mark=None,
                flow_style=start_event.flow_style)
        # node.add_node(1, bipartite=1)
        # node.add_edge(0, 1, direction="head")
        if anchor is not None:
            self.anchors[anchor] = node
        index = 0
        relabel_label = 2
        prev_labels = [1]
        while not self.check_event(SequenceEndEvent):
            index += 1
            item_label = relabel_label
            item = nx.relabel.convert_node_labels_to_integers(
                self.compose_node(node, index), item_label)
            node = nx.union(node, item)
            relabel_label += item.number_of_nodes()
            for l in prev_labels:
                node.add_edge(l, item_label, direction="tail")
            # node.add_edge(prev_label, item_label, direction="tail")
            # prev_label = item_label
            prev_labels = item[item_label]
        end_event = self.get_event()
        node.end_mark = end_event.end_mark
        return node

    def compose_mapping_node(self, anchor):
        start_event = self.get_event()
        tag = start_event.tag
        if tag is None or tag == '!':
            tag = self.resolve("mapping", None, start_event.implicit)
        node = nx.MultiGraph(**{"kind": "mapping", "network-type": "directed"})
        node.add_node(0, bipartite=0, kind="mapping", tag=tag,
                start_mark=start_event.start_mark,
                end_mark=None,
                flow_style=start_event.flow_style)
        node.add_node(1, bipartite=1)
        node.add_edge(0, 1, direction="tail")
        if anchor is not None:
            self.anchors[anchor] = node
        relabel_label = 2
        key_labels = []
        while not self.check_event(MappingEndEvent):
            #key_event = self.peek_event()
            key_label = relabel_label
            item_key = nx.relabel.convert_node_labels_to_integers(
                self.compose_node(node, None), key_label)
            relabel_label += item_key.number_of_nodes()
            value_label = relabel_label
            item_value = nx.relabel.convert_node_labels_to_integers(
                self.compose_node(node, item_key), value_label)
            #if item_key in node.value:
            #    raise ComposerError("while composing a mapping", start_event.start_mark,
            #            "found duplicate key", key_event.start_mark)
            #node.value[item_key] = item_value
            node = nx.union(node, item_key)
            # node.add_edge(0, key_label + 1, direction="tail")
            node.add_edge(1, key_label,direction="head")
            # for l in item_key[key_label]:
            #     node.add_edge(0, l, direction="tail")
            if not (item_value.nodes[value_label]["kind"] == "scalar" and not item_value.nodes[value_label].get("value")):
                node = nx.union(node, item_value)
                relabel_label += item_value.number_of_nodes()
                # node.add_edge(1, key_label, direction="tail")
                # node.add_edge(key_label + 1, value_label, direction="tail")
                for l in item_key[key_label]:
                    for l2 in item_key[l]:
                        if l2 != key_label:
                            node.add_edge(value_label + 1, l2, direction="tail")
                # for l in item_value[value_label]:
                #     node.add_edge(key_label, l, direction="tail")
            key_labels.append(key_label)
            # TODO if head or tail
            # u_tail = [e for _, e, d in node.edges(u, data="direction") if d == "tail"]
        #     # v_head = [e for _, e, d in node.edges(v, data="direction") if d == "head"]
        # if not key_labels:
        #     node.add_edge(0, 1, direction="tail")
        #     node.add_node(relabel_label, bipartite=1)
        #     node.add_edge(relabel_label, 0, direction="tail")
        #     relabel_label += 1
        # for k1, k2 in combinations(key_labels, 2):
        #     node.add_edge(k1, k2 + 1, direction="tail")
        #     node.add_edge(k2, k1 + 1, direction="tail")
        # for k1 in key_labels:
        #     node.add_edge(k1 + 1, 0, direction="tail")
        end_event = self.get_event()
        node.end_mark = end_event.end_mark
        return node

