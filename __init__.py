
__all__ = [
    'NxSafeLoader', 'NxSafeDumper'
]

from yaml._yaml import CEmitter, CParser

from .composer import *
from .constructor import *
from .representer import *
from .resolver import *
from .serializer import *

class NxSafeLoader(CParser, NxSafeConstructor, NxResolver):

    def __init__(self, stream):
        CParser.__init__(self, stream)
        NxSafeConstructor.__init__(self)
        NxResolver.__init__(self)

class NxSafeDumper(CEmitter, NxSafeRepresenter, NxResolver):

    def __init__(self, stream,
            default_style=None, default_flow_style=False,
            canonical=None, indent=None, width=None,
            allow_unicode=None, line_break=None,
            encoding=None, explicit_start=None, explicit_end=None,
            version=None, tags=None, sort_keys=True):
        CEmitter.__init__(self, stream, canonical=canonical,
                indent=indent, width=width, encoding=encoding,
                allow_unicode=allow_unicode, line_break=line_break,
                explicit_start=explicit_start, explicit_end=explicit_end,
                version=version, tags=tags)
        NxSafeRepresenter.__init__(self, default_style=default_style,
                default_flow_style=default_flow_style, sort_keys=sort_keys)
        NxResolver.__init__(self)
