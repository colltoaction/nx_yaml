import networkx as nx


def sequence_append(self, node: nx.DiGraph):
    relabel_label = self.graph.number_of_nodes()
    item_label = relabel_label
    other_graph = nx.relabel.convert_node_labels_to_integers(node.graph, item_label)
    new_graph = nx.union(self.graph, other_graph)
    relabel_label += other_graph.number_of_nodes()
    pair_label = relabel_label
    # TODO consider how connecting each open out-port
    # is different from the spec but visually better
    relabel_label += 1
    for n, b in self.graph.nodes(data="bipartite"):
        if b == 1 and self.graph.out_degree(n) == 1 and self.graph.in_degree(n) == 0:
            new_graph.add_edge(n, item_label)
    self.graph = new_graph

def mapping_append(self, item_key: nx.DiGraph, item_value: nx.DiGraph):
    relabel_label = self.graph.number_of_nodes()
    # pair_label = relabel_label
    # self.graph.add_node(pair_label, bipartite=1)
    # relabel_label += 1
    # if self.prev_label:
    #     self.graph.add_edge(pair_label, self.prev_label)
    #key_event = self.peek_event()
    key_label = relabel_label
    item_key_graph = nx.relabel.convert_node_labels_to_integers(item_key.graph, key_label)
    relabel_label += item_key_graph.number_of_nodes()
    value_label = relabel_label
    item_value_graph = nx.relabel.convert_node_labels_to_integers(item_value.graph, value_label)
    new_graph = nx.union(self.graph, item_key_graph)
    new_graph.add_edge(1, key_label)
    # new_graph.add_edge(pair_label, key_label, direction="tail")
    if not (item_value_graph.nodes[value_label]["kind"] == "scalar" and not item_value_graph.nodes[value_label].get("value")):
        new_graph = nx.union(new_graph, item_value_graph)
        relabel_label += item_value_graph.number_of_nodes()
        # new_graph.add_edge(value_label, pair_label)
        # TODO for each hyperedge with out degree 0
        for n, b in item_key_graph.nodes(data="bipartite"):
            if b == 1 and item_key_graph.out_degree(n) == 1 and item_key_graph.in_degree(n) == 0:
                new_graph.add_edge(n, value_label)
    self.prev_label = relabel_label
    self.graph = new_graph
