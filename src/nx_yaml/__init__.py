
__all__ = [
    'NxSafeLoader', 'NxSafeDumper'
]

import io

from yaml.constructor import SafeConstructor
from yaml.reader import Reader
from yaml.representer import SafeRepresenter
from yaml.resolver import BaseResolver

from .composer import NxComposer
from .scanner import NxScanner
from .serializer import NxSerializer

# TODO using CParser doesn't integrate well
class NxSafeLoader(Reader, NxScanner, NxComposer, SafeConstructor, BaseResolver):

    def __init__(self, stream):
        Reader.__init__(self, stream)
        NxScanner.__init__(self)
        NxComposer.__init__(self)
        SafeConstructor.__init__(self)
        BaseResolver.__init__(self)

class NxSafeDumper(NxSerializer):
    def __init__(self, stream):
        NxSerializer.__init__(self, stream)


def nx_compose_all(stream):
    """
    Parse all YAML documents in a stream
    and produce a single hypergraph with syntax and structure.
    """
    loader = NxSafeLoader(stream)
    return loader.compose_stream()

def nx_serialize_all(node):
    """
    Serialize a single hypergraph with syntax and structures into a YAML stream.
    If stream is None, return the produced string instead.
    """
    stream = io.StringIO()
    dumper = NxSafeDumper(stream)
    dumper.emit_node(node, 0, 0)
    return stream.getvalue()
