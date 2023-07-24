# nx_yaml

A library for loading a YAML [Representation Graph] into NetworkX.

## Development

This is a work in progress POC.
`pypi` is updated on demand.

The development environment is self-contained using the `pipenv` tool.

## Testing

* Create YAML and GML files in `resources/tests`.
* Write graph tests using `pytest`.

## Design

### YAML Representation Graph

The Representation Graph is a well-defined subsection of the YAML specification.
This library reads YAML and instantiates this graph using NetworkX.

The YAML document is in one-to-one correspondence with this NetworkX graph.
This means we can go back and forth freely between the two.

We expect humans to find this language friendly!

> **Note on NetworkX versions < 3**
> The `read_yaml` and `write_yaml` functions worked completely different from this implementation.
> and are not related in any way to this project.

[Representation Graph]: https://yaml.org/spec/1.2-old/spec.html#id2763754
