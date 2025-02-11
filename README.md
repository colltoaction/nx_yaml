# nx_yaml
`nx_yaml` is a general purpose Hypergraph Intermediate Representation for [YAML](https://yaml.org/spec/1.2.2) using [NetworkX](https://github.com/networkx/networkx). It provides native semantics for higher-order applications such as Hypergraph Analysis, Quantum Computing, Geometric Deep Learning and Monoidal Computing.

There are two notebook tutorials: [a basic one](tutorial.ipynb) and an advanced one using [XGI](xgi.ipynb) for higher-order interpretation.

## Design
Graph Theory is well established in compiler infrastructure, popularized by the use of Abstract Syntax Trees, and recently projects such as [MLIR](https://mlir.llvm.org/docs/Rationale/RationaleGenericDAGRewriter/) have further explored Direct Acyclic Graphs. This project formalizes a [Hypergraph](https://en.wikipedia.org/wiki/Hypergraph) IR with native semantics for higher-order applications such as:
* Hypergraph Analysis: https://github.com/pnnl/HyperNetX
* Quantum Computing: https://github.com/zxcalc/pyzx
* Geometric Deep Learning: https://github.com/pyg-team/pytorch_geometric
* Monoidal Computing: https://github.com/discopy/discopy

YAML has the advantage of being a widely known syntax that is implemented in all programming languages. NetworkX enables seamless collaboration between graph libraries. We can implement all sorts of document transformations, leveraging a large ecosystem of software and well-known algorithms for complex networks.

## Implementation
This project implements the PyYAML `yaml.compose` and `yaml.serialize` APIs using the NetworkX graph library.
`compose` takes text input and converts it to a graph, while `serialize` does the inverse operation.
Understanding this data structure is key to create portable and correct tooling for YAML, moving freely between text-based and code representations.

Check out the [notebook tutorial](tutorial.ipynb).
We use `NxSafeLoader` and `NxSafeDumper` with the PyYAML `yaml.compose` and `yaml.serialize` APIs.

### Milestone 1

1. Copy and paste from PyYAML
1. Replace uses of `nodes` with NetworkX
1. Publish a drop-in pip replacement

### Milestone 2

1. Compare performance
1. Compare alignment with spec
1. Share findings

## Development environment

This is work in progress.
`pypi` is updated on demand.

The development environment is self-contained using the `pipenv` tool.

### Testing

* Just `pytest`
* Store graphs in `resources/tests`


[Representation Graph]: https://yaml.org/spec/1.2.2/#321-representation-graph
[pyyaml.nodes]: https://github.com/yaml/pyyaml/blob/main/lib/yaml/nodes.py
