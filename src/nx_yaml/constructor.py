
__all__ = [
    'NxSafeConstructor',
]

import itertools
from yaml.constructor import ConstructorError

import networkx as nx

class NxSafeConstructor:
    def check_data(self):
        # If there are more documents available?
        return self.check_node()

    def get_data(self):
        # Construct and return the next document.
        if self.check_node():
            return self.construct_document(self.get_node())

    def get_single_data(self):
        # Ensure that the stream contains a single document and construct it.
        node = self.get_single_node()
        if node is not None:
            return self.construct_document(node)
        return None

    def construct_document(self, node: nx.DiGraph):
        data = self.construct_object(node)
        return data

    def construct_object(self, node: nx.DiGraph):
        # TODO should always be a digraph
        match node:
            case nx.DiGraph():
                match node.graph:
                    case {"kind": "scalar"}:
                        return self.construct_scalar(node)
                    case {"kind": "sequence"}:
                        return self.construct_sequence(node) or \
                                self.construct_mapping(node)
                    case {"kind": "mapping"}:
                        return self.construct_mapping(node)
                    case _:
                        # guess the simplest representation
                        return self.construct_scalar(node) or \
                                self.construct_sequence(node) or \
                                self.construct_mapping(node) or \
                                None
            case _: return node

    def construct_scalar(self, node: nx.DiGraph):
        if nx.is_empty(node):
            return ''
        match list(node.edges):
            case [(s, None)] | [(None, s)]: return s
            case [_]: return None
        match list(node.nodes):
            case [n]: return n
        return None

    def construct_sequence(self, node: nx.DiGraph) -> tuple:
        if not nx.is_directed_acyclic_graph(node):
            print(node)
            return None
        # TODO build paths from roots
        nodes = tuple(nx.topological_sort(node))
        if nx.is_path(node, nodes):
            return nodes
        return None
        # quiero un mapping porque left apunta a right")
        return tuple(
            self.construct_object(node.subgraph([left] + list(node.successors(left))))
            for left in nodes
            if node.in_degree(left) == 0)

    def construct_mapping(self, node: nx.DiGraph):
        """"""
        match list(node.nodes):
            case []: return { }
            case [n]: return { n: n if len(node.edges) == 1 else None }
        match list(node.edges):
            case []:
                return { n: None for n in node.nodes }
        return {
            n: self.construct_object(node.subgraph(node.successors(n)))
            for n in node.nodes
            if node.out_degree(n) > 0 }
        # match list(nx.algorithms.cycles.simple_cycles(node)):
        #     case []:
        #     case cycles:
        #         return {
        #             node: node
        #             for cycle in cycles
        #             for node in cycle
        #         }
