# nx_yaml

Intermediate Representation for YAML documents using NetworkX.

The YAML language has the flexibility to model all sorts of native data types across programming languages,
with its power coming in part from the graph model behind every document.
Understanding this data structure is key to create portable and correct tooling for YAML.

Graph Theory is well established in compiler infrastructure in the use of Abstract Syntax Trees.
It is tempting to use them to model the YAML language but we have found them to be unfit.
We chose [Incidence Graphs] because we need to support cycles, recursivity and other features
that one doesn't see in traditional programming languages but make sense in this data language.

## Quickstart

Check the [notebook tutorial](tutorial.ipynb) for nice graph pictures!

```py
import yaml
from nx_yaml import NxSafeLoader
import networkx as nx
import matplotlib.pyplot as plt

data_out = yaml.compose("Hello: World!", Loader=NxSafeLoader)
nx.draw_spectral(data_out, with_labels=True, node_size=5000)
plt.show()
```

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
[Incidence Graphs]: https://en.wikipedia.org/wiki/Levi_graph
