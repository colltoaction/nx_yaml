import networkx as nx
import yaml
from yaml.nodes import *


representer = yaml.representer.Representer()
constructor = yaml.constructor.Constructor()


def to_nx_graph(node: Node) -> nx.DiGraph:
    digraph = None
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
        case MappingNode():
            node_as_dict = constructor.construct_mapping(node)
            return nx.DiGraph([
                (source, target)
                for source, target in node_as_dict.items()
            ])
        case _:
            assert node is None
    return digraph


def to_yaml_node(digraph: nx.DiGraph) -> Node:
    if not isinstance(digraph, nx.Graph):
        return representer.represent_str(digraph)
    if len(digraph.nodes) == 0:
        return representer.represent_none(None)
    if len(digraph.nodes) == 1:
        if len(digraph.edges) == 0:
            node = next(iter(digraph))
            return representer.represent_str(node)
    if nx.is_empty(digraph):
        return representer.represent_set({node for node in digraph})
    if not nx.is_empty(digraph):
        return representer.represent_dict({
                source: target
                for (source, target) in digraph.edges
        })
    assert digraph is None
