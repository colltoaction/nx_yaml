
__all__ = [
    'NxSafeLoader', 'NxSafeDumper'
]

from yaml._yaml import CEmitter, CParser
from yaml.parser import Parser
from yaml.emitter import Emitter
from yaml.reader import Reader
from yaml.scanner import Scanner

from .composer import NxComposer
from .constructor import NxSafeConstructor
from .representer import NxSafeRepresenter
from .resolver import NxResolver
from .serializer import NxSerializer

# TODO using CParser doesn't integrate well
class NxSafeLoader(Reader, Scanner, Parser, NxComposer, NxSafeConstructor, NxResolver):

    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        NxComposer.__init__(self)
        NxSafeConstructor.__init__(self)
        NxResolver.__init__(self)

class NxSafeDumper(Emitter, NxSerializer, NxSafeRepresenter, NxResolver):

    def __init__(self, stream,
            default_style=None, default_flow_style=False,
            canonical=None, indent=None, width=None,
            allow_unicode=None, line_break=None,
            encoding=None, explicit_start=None, explicit_end=None,
            version=None, tags=None, sort_keys=True):
        Emitter.__init__(self, stream, canonical=canonical,
                indent=indent, width=width,
                allow_unicode=allow_unicode, line_break=line_break)
        NxSerializer.__init__(self, encoding=encoding,
                explicit_start=explicit_start, explicit_end=explicit_end,
                version=version, tags=tags)
        NxSafeRepresenter.__init__(self, default_style=default_style,
                default_flow_style=default_flow_style, sort_keys=sort_keys)
        NxResolver.__init__(self)
