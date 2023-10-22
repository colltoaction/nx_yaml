# nx_yaml

Fast [Representation Graph] for PyYAML using NetworkX.

## Design

### All users

This library offers four implementations that jointly bypass the [yaml.nodes] library. This is transparent to users of `load` and `dump` since the representation graph is an implementation detail. This library will be faster thanks to a better graph implementation.

### Graph users

Users of graphs who use the `compose` and `represent` will now get NetworkX objects. NX is a fully fledged library compared to the barebones `yaml.nodes` module.

With `nx_yaml` NetworkX becomes your native representation graph using YAML. There is no need to convert between the `yaml.nodes.Node` and `nx.DiGraph` by hand.

See:
* https://github.com/yaml/pyyaml/issues/757

## Implementation

### Milestone 1

1. Copy and paste from PyYAML
1. Replace uses of `nodes`
1. Publish a drop-in `yaml` replacement

* `NxComposer`: https://github.com/yaml/pyyaml/blob/main/lib/yaml/composer.py
* `NxConstructor`: https://github.com/yaml/pyyaml/blob/main/lib/yaml/constructor.py
* `NxRepresenter`: https://github.com/yaml/pyyaml/blob/main/lib/yaml/representer.py
* `NxSerializer`: https://github.com/yaml/pyyaml/blob/main/lib/yaml/serializer.py

With these and `CEmitter` and `CParser` from [LibYAML](https://pyyaml.org/wiki/LibYAML) we use all fast, native library bindings in the full load/dump cycle.

### Milestone 2

1. Evaluate adoption
1. Evaluate performance
1. Propose these changes upstream

## Development environment

This is work in progress.
`pypi` is updated on demand.

The development environment is self-contained using the `pipenv` tool.

### Testing

* Create YAML and GML files in `resources/tests`.
* Write graph tests using `pytest`.


[Representation Graph]: https://yaml.org/spec/1.2.2/#321-representation-graph
[yaml.nodes]: https://github.com/yaml/pyyaml/blob/main/lib/yaml/nodes.py
