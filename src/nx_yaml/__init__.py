
__all__ = [
    'NxSafeLoader', 'NxSafeDumper'
]

import io

from yaml.reader import Reader

from .scanner import NxScanner
from .serializer import NxSerializer

class NxSafeLoader(Reader, NxScanner):
    def __init__(self, stream):
        Reader.__init__(self, stream)
        NxScanner.__init__(self)

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
