# nx_yaml

Fast, native NetworkX support for PyYAML.

## Development

This is work in progress.
`pypi` is updated on demand.

The development environment is self-contained using the `pipenv` tool.

## Testing

* Create YAML and GML files in `resources/tests`.
* Write graph tests using `pytest`.

## Design

With this library we offer four implementations that jointly bypass the `nodes` library and use NetworkX.

* `NxComposer`: https://github.com/yaml/pyyaml/blob/main/lib/yaml/composer.py
* `NxConstructor`: https://github.com/yaml/pyyaml/blob/main/lib/yaml/constructor.py
* `NxRepresenter`: https://github.com/yaml/pyyaml/blob/main/lib/yaml/representer.py
* `NxSerializer`: https://github.com/yaml/pyyaml/blob/main/lib/yaml/serializer.py

With these four classes and `CEmitter` and `CParser` from [LibYAML](https://pyyaml.org/wiki/LibYAML) we use all fast, native library bindings.

# NetworkX syntax

> **Note on NetworkX versions < 3**
> The `read_yaml` and `write_yaml` functions worked completely different from this implementation.
> and are not related in any way to this project.

With this approach NetworkX becomes the native PyYAML representation graph.

[Representation Graph]: https://yaml.org/spec/1.2-old/spec.html#id2763754
