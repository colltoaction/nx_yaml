import networkx as nx


def sequence_append(graph: nx.DiGraph, node: nx.DiGraph):
    relabel_label = graph.number_of_nodes()
    item_label = relabel_label
    other_graph = nx.relabel.convert_node_labels_to_integers(node, item_label)
    new_graph = nx.union(graph, other_graph)
    relabel_label += other_graph.number_of_nodes()
    pair_label = relabel_label
    # TODO consider how connecting each open out-port
    # is different from the spec but visually better
    relabel_label += 1
    for n, b in graph.nodes(data="bipartite"):
        if b == 1 and graph.out_degree(n) == 1 and graph.in_degree(n) == 0:
            new_graph.add_edge(n, item_label)

def sequence_append(graph: nx.DiGraph, item: nx.DiGraph):
    relabel_label = graph.number_of_nodes()
    label = relabel_label
    item_graph = nx.relabel.convert_node_labels_to_integers(item, label)
    relabel_label += item_graph.number_of_nodes()
    new_graph = nx.union(graph, item_graph)
    new_graph.add_edge(1, label)
    return new_graph

def mapping_append(graph: nx.DiGraph, item_key: nx.DiGraph, item_value: nx.DiGraph):
    relabel_label = graph.number_of_nodes()
    key_label = relabel_label
    item_key_graph = nx.relabel.convert_node_labels_to_integers(item_key, key_label)
    relabel_label += item_key_graph.number_of_nodes()
    value_label = relabel_label
    item_value_graph = nx.relabel.convert_node_labels_to_integers(item_value, value_label)
    new_graph = nx.union(graph, item_key_graph)
    new_graph.add_edge(1, key_label)
    if not (item_value_graph.nodes[value_label]["kind"] == "scalar" and not item_value_graph.nodes[value_label].get("value")):
        new_graph = nx.union(new_graph, item_value_graph)
        relabel_label += item_value_graph.number_of_nodes()
        new_graph.add_edge(1, value_label, direction="tail")
    return new_graph
