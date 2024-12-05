import networkx as nx


class Node(object):
    def __init__(self, tag, value, start_mark, end_mark):
        self.tag = tag
        self.value = value
        self.start_mark = start_mark
        self.end_mark = end_mark

class ScalarNode(Node):
    id = 'scalar'
    def __init__(self, tag, value,
            start_mark=None, end_mark=None, style=None):
        self.graph = nx.MultiGraph(**{"kind": "scalar", "network-type": "directed"})
        self.graph.add_node(0, bipartite=0,
                kind="scalar", tag=tag, value=value,
                start_mark=start_mark,
                end_mark=end_mark,
                flow_style=style)

class CollectionNode(Node):
    pass

class SequenceNode(CollectionNode):
    id = 'sequence'  
    def __init__(self, tag, value,
            start_mark=None, end_mark=None, flow_style=None):
        self.graph = nx.MultiGraph(**{"kind": "sequence", "network-type": "directed"})
        self.graph.add_node(0, bipartite=0,
                kind="sequence", tag=tag,
                start_mark=start_mark,
                end_mark=end_mark,
                flow_style=flow_style)
        self.graph.add_node(1, bipartite=1)
        self.graph.add_edge(0, 1, direction="tail")
        self.prev_label = 0

    def append(self, node: Node):
        relabel_label = self.graph.number_of_nodes()
        item_label = relabel_label
        other_graph = nx.relabel.convert_node_labels_to_integers(node.graph, item_label)
        new_graph = nx.union(self.graph, other_graph)
        relabel_label += other_graph.number_of_nodes()
        pair_label = relabel_label
        new_graph.add_node(pair_label, bipartite=1)
        new_graph.add_edge(1, item_label)
        relabel_label += 1
        if self.prev_label:
            new_graph.add_edge(pair_label, self.prev_label, direction="tail")
            new_graph.add_edge(pair_label, item_label)
        self.prev_label = item_label
        self.graph = new_graph

class MappingNode(CollectionNode):
    id = 'mapping'

    def __init__(self, tag, value,
            start_mark=None, end_mark=None, flow_style=None):
        self.graph = nx.MultiGraph(**{"kind": "mapping", "network-type": "directed"})
        self.graph.add_node(0, bipartite=0,
                kind="mapping", tag=tag,
                start_mark=start_mark,
                end_mark=end_mark,
                flow_style=flow_style)
        self.graph.add_node(1, bipartite=1)
        self.graph.add_edge(0, 1)

    def append(self, item_key: Node, item_value: Node):
        relabel_label = self.graph.number_of_nodes()
        pair_label = relabel_label
        self.graph.add_node(pair_label, bipartite=1)
        relabel_label += 1
        self.graph.add_edge(pair_label, 0)
        #key_event = self.peek_event()
        key_label = relabel_label
        item_key_graph = nx.relabel.convert_node_labels_to_integers(item_key.graph, key_label)
        relabel_label += item_key_graph.number_of_nodes()
        value_label = relabel_label
        item_value_graph = nx.relabel.convert_node_labels_to_integers(item_value.graph, value_label)
        new_graph = nx.union(self.graph, item_key_graph)
        new_graph.add_edge(1, key_label)
        new_graph.add_edge(pair_label, key_label)
        if not (item_value_graph.nodes[value_label]["kind"] == "scalar" and not item_value_graph.nodes[value_label].get("value")):
            new_graph = nx.union(new_graph, item_value_graph)
            relabel_label += item_value_graph.number_of_nodes()
            new_graph.add_edge(value_label, pair_label)
        self.graph = new_graph
