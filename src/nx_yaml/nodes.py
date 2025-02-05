import networkx as nx


def sequence_append(graph: nx.DiGraph, item: nx.DiGraph):
    label = graph.number_of_nodes()
    item_graph = nx.relabel.convert_node_labels_to_integers(item, label)
    # new_graph = nx.union(graph, item_graph)
    graph.update(item_graph)
    graph.add_edge(1, label)
    # return new_graph

def mapping_append(graph: nx.DiGraph, item_key: nx.DiGraph, item_value: nx.DiGraph):
    relabel_label = graph.number_of_nodes()
    key_label = relabel_label
    item_key_graph = nx.relabel.convert_node_labels_to_integers(item_key, key_label)
    relabel_label += item_key_graph.number_of_nodes()
    value_label = relabel_label
    item_value_graph = nx.relabel.convert_node_labels_to_integers(item_value, value_label)
    graph.update(item_key_graph)
    graph.update(item_value_graph)
    # new_graph = nx.union(graph, item_key_graph)
    graph.add_edge(1, key_label)
    # new_graph = nx.union(new_graph, item_value_graph)
    graph.add_edge(1, value_label, direction="tail")
    # return new_graph
