# nx_yaml

Intermediate Representation for YAML documents using NetworkX.

## Design
The YAML language has the flexibility to model all sorts of data across programming languages,
with its power coming in part from the graph model behind every document.
Graph Theory is well established in compiler infrastructure, popularized by the use of Abstract Syntax Trees.
We chose [Incidence Graphs] over ASTs for YAML because we need to support cycles, recursivity and other features that one doesn't see in traditional programming languages.
Understanding this data structure is key to create portable and correct tooling for YAML, moving freely between text-based and abstract representations.

## Implementation
This project implements the PyYAML `yaml.compose` and `yaml.serialize` APIs using the NetworkX graph library.
`compose` takes text input and converts it to a graph, while `serialize` does the inverse operation.
Using NetworkX graphs we can implement all sorts of document transformations, leveraging a large ecosystem of software and well-known algorithms for complex networks.

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
[Incidence Graphs]: https://en.wikipedia.org/wiki/Levi_graph
