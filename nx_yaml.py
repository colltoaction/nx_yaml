import networkx as nx
import yaml
from yaml.nodes import *


def to_digraph(node: Node) -> nx.DiGraph:
    match node:
        case None | ScalarNode(tag="tag:yaml.org,2002:null"):
            digraph = nx.null_graph()
        case ScalarNode(value=scalar):
            scalar_node = yaml.safe_load(scalar)
            digraph = nx.DiGraph()
            digraph.add_node(scalar_node)
        case SequenceNode(value=path):
            # compose is not enough
            digraph = nx.compose_all(to_digraph(n) for n in path)
        case MappingNode(value=edges):
            digraph = nx.compose_all(
                nx.compose(to_digraph(s), to_digraph(t))
                for (s, t) in edges)
    return digraph