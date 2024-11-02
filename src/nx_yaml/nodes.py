

def add_data_edge(node, head, tail):
    edge_id = node.number_of_nodes()
    node.add_node(edge_id, bipartite=1)
    for n, b in head.nodes(data="bipartite"):
        if b == 0:
            node.add_edge(edge_id, n, direction="head")
    for n, b in tail.nodes(data="bipartite"):
        if b == 0:
            node.add_edge(edge_id, n, direction="tail")
    return node