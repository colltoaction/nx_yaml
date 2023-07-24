# nx_yaml

This library brings a new approach to use NetworkX graphs with YAML.

## YAML Representation Graph

The [Representation Graph] is a 

Previous to NetworkX v3 the `read_yaml` and `write_yaml` were included.
These were tied to the native python data structures and default serialization.
Instead of using `yaml.load` we will focus con `yaml.compose`, which exposes the underlying document graph.

This new approach allows us to manipulate YAML documents using NetworkX.
The representation graph is in one-to-one correspondence with a NetworkX graph,
so we can use this language to specify graphs in human-friendly fashion.

This library also bridges the gap for `NetworkX<v3`.


[Representation Graph]: https://yaml.org/spec/1.2-old/spec.html#id2763754
