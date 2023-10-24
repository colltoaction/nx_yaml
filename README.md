# nx_yaml

Fast [Representation Graph] for PyYAML using NetworkX.

## Design

### All users

This library offers four implementations that jointly bypass the [pyyaml.nodes] library. This is transparent when you use `load` and `dump` since the representation graph is an implementation detail. This library will be faster thanks to a better graph implementation.

### Graph users

Users of graphs who use the `compose` and `represent` will now get NetworkX objects. NX is a fully fledged library compared to the barebones `yaml.nodes` module.

With `nx_yaml` NetworkX becomes your native representation graph using YAML. There is no need to convert between the `yaml.nodes.Node` and `nx.DiGraph` by hand.

See:
* https://github.com/yaml/pyyaml/issues/757

## Implementation

![RGraph](https://github.com/yaml-programming/nx_yaml/assets/1548532/6423f4a4-ea2f-4397-9973-540c0a57cec7)

Four abstraction isolate and replace [pyyaml.nodes] representation graph implementation:
* `NxComposer`: https://github.com/yaml/pyyaml/blob/main/lib/yaml/composer.py
* `NxConstructor`: https://github.com/yaml/pyyaml/blob/main/lib/yaml/constructor.py
* `NxRepresenter`: https://github.com/yaml/pyyaml/blob/main/lib/yaml/representer.py
* `NxSerializer`: https://github.com/yaml/pyyaml/blob/main/lib/yaml/serializer.py

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
