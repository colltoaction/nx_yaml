import networkx as nx
import yaml
from yaml.nodes import *


def to_nx_graph(node: Node) -> nx.DiGraph:
    match node:
        case None | ScalarNode(tag="tag:yaml.org,2002:null"):
            digraph = nx.null_graph()
        case ScalarNode(value=scalar):
            scalar_node = yaml.safe_load(scalar)
            digraph = nx.DiGraph()
            digraph.add_node(scalar_node)
        case SequenceNode(value=path):
            # compose is not enough
            digraph = nx.compose_all(to_nx_graph(n) for n in path)
        case MappingNode(value=edges):
            digraph = nx.compose_all(
                nx.compose(to_nx_graph(s), to_nx_graph(t))
                for (s, t) in edges)
    return digraph


def to_yaml_node(digraph: nx.DiGraph) -> Node:
    return ScalarNode(tag="tag:yaml.org,2002:null", value="~")

def yaml_nodes_equal(node1: Node, node2: Node):
    if "tag:yaml.org,2002:null" == node1.tag == node2.tag:
        return True
    return False