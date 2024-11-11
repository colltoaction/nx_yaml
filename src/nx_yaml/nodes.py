"""
The YAML Representation Graph is
implemented using bipartite multigraph:
* nodes bipartite=0 are scalar nodes
* nodes bipartite=1 are edges in a collection node
* real edges are incidences
* the root is the edge at node 0
We can easily merge many multigraphs
with edges between root objects
https://yaml.org/spec/1.2.2/#321-representation-graph
"""
import networkx as nx


def iter_sequence(seq: nx.MultiGraph, root):
    """A sequence has zero or more natural-number-labelled edges to its children."""
    assert seq.nodes[root]["kind"] == "sequence"
    hyperedges = sorted(seq[root])
    for h in hyperedges:
        [e1, e2] = seq[h]
        n = e1 if e2 == root else e2
        assert n["direction"] == "tail"
        yield n
