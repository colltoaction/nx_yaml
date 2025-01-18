
__all__ = [
    'NxSafeLoader', 'NxSafeDumper'
]

from yaml.parser import Parser
from yaml.constructor import SafeConstructor
from yaml.reader import Reader
from yaml.representer import SafeRepresenter
from yaml.resolver import BaseResolver
from yaml.scanner import Scanner

from .composer import NxComposer
from .emitter import NxEmitter
from .serializer import NxSerializer

# TODO using CParser doesn't integrate well
class NxSafeLoader(Reader, Scanner, Parser, NxComposer, SafeConstructor, BaseResolver):

    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        NxComposer.__init__(self)
        SafeConstructor.__init__(self)
        BaseResolver.__init__(self)

class NxSafeDumper(NxEmitter, NxSerializer, SafeRepresenter, BaseResolver):

    def __init__(self, stream,
            default_style=None, default_flow_style=False,
            canonical=None, indent=None, width=None,
            allow_unicode=None, line_break=None,
            encoding=None, explicit_start=None, explicit_end=None,
            version=None, tags=None, sort_keys=True):
        NxEmitter.__init__(self, stream, canonical=canonical,
                indent=indent, width=width,
                allow_unicode=allow_unicode, line_break=line_break)
        NxSerializer.__init__(self, encoding=encoding,
                explicit_start=explicit_start, explicit_end=explicit_end,
                version=version, tags=tags)
        SafeRepresenter.__init__(self, default_style=default_style,
                default_flow_style=default_flow_style, sort_keys=sort_keys)
        BaseResolver.__init__(self)
