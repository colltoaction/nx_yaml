
__all__ = [
    'NxSafeConstructor',
]

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
        match node.graph.get("kind", None):
            case "scalar": data = self.construct_scalar(node)
            case "sequence": data = self.construct_sequence(node)
            case _: data = self.construct_mapping(node)
        if isinstance(data, types.GeneratorType):
            generator = data
            data = next(generator)
            self.state_generators.append(generator)
        self.constructed_objects[node] = data
        del self.recursive_objects[node]
        return data

    def construct_scalar(self, node: nx.DiGraph):
        """node is a digraph with no annotations"""
        if node.edges:
            return None
        match tuple(iter(node.nodes)):
            case ( ): return ''
            case (value, ): return value
            case _: return None

    def construct_sequence(self, node: nx.DiGraph):
        return tuple(
            self.construct_object(child)
            for child in node.value)

    def construct_mapping(self, node: nx.DiGraph):
        """"""
        match list(nx.algorithms.cycles.simple_cycles(node)):
            case []:
                match list(node.edges):
                    case []:
                        return {}
                    case edges:
                        return { src: tgt for src, tgt in edges }
            case cycles:
                return {
                    node: node
                    for cycle in cycles
                    for node in cycle
                }
