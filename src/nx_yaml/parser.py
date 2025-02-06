
# The following YAML grammar is LL(1) and is parsed by a recursive descent
# parser.
#
# stream            ::= STREAM-START implicit_document? explicit_document* STREAM-END
# implicit_document ::= block_node DOCUMENT-END*
# explicit_document ::= DIRECTIVE* DOCUMENT-START block_node? DOCUMENT-END*
# block_node_or_indentless_sequence ::=
#                       ALIAS
#                       | properties (block_content | indentless_block_sequence)?
#                       | block_content
#                       | indentless_block_sequence
# block_node        ::= ALIAS
#                       | properties block_content?
#                       | block_content
# flow_node         ::= ALIAS
#                       | properties flow_content?
#                       | flow_content
# properties        ::= TAG ANCHOR? | ANCHOR TAG?
# block_content     ::= block_collection | flow_collection | SCALAR
# flow_content      ::= flow_collection | SCALAR
# block_collection  ::= block_sequence | block_mapping
# flow_collection   ::= flow_sequence | flow_mapping
# block_sequence    ::= BLOCK-SEQUENCE-START (BLOCK-ENTRY block_node?)* BLOCK-END
# indentless_sequence   ::= (BLOCK-ENTRY block_node?)+
# block_mapping     ::= BLOCK-MAPPING_START
#                       ((KEY block_node_or_indentless_sequence?)?
#                       (VALUE block_node_or_indentless_sequence?)?)*
#                       BLOCK-END
# flow_sequence     ::= FLOW-SEQUENCE-START
#                       (flow_sequence_entry FLOW-ENTRY)*
#                       flow_sequence_entry?
#                       FLOW-SEQUENCE-END
# flow_sequence_entry   ::= flow_node | KEY flow_node? (VALUE flow_node?)?
# flow_mapping      ::= FLOW-MAPPING-START
#                       (flow_mapping_entry FLOW-ENTRY)*
#                       flow_mapping_entry?
#                       FLOW-MAPPING-END
# flow_mapping_entry    ::= flow_node | KEY flow_node? (VALUE flow_node?)?
#
# FIRST sets:
#
# stream: { STREAM-START }
# explicit_document: { DIRECTIVE DOCUMENT-START }
# implicit_document: FIRST(block_node)
# block_node: { ALIAS TAG ANCHOR SCALAR BLOCK-SEQUENCE-START BLOCK-MAPPING-START FLOW-SEQUENCE-START FLOW-MAPPING-START }
# flow_node: { ALIAS ANCHOR TAG SCALAR FLOW-SEQUENCE-START FLOW-MAPPING-START }
# block_content: { BLOCK-SEQUENCE-START BLOCK-MAPPING-START FLOW-SEQUENCE-START FLOW-MAPPING-START SCALAR }
# flow_content: { FLOW-SEQUENCE-START FLOW-MAPPING-START SCALAR }
# block_collection: { BLOCK-SEQUENCE-START BLOCK-MAPPING-START }
# flow_collection: { FLOW-SEQUENCE-START FLOW-MAPPING-START }
# block_sequence: { BLOCK-SEQUENCE-START }
# block_mapping: { BLOCK-MAPPING-START }
# block_node_or_indentless_sequence: { ALIAS ANCHOR TAG SCALAR BLOCK-SEQUENCE-START BLOCK-MAPPING-START FLOW-SEQUENCE-START FLOW-MAPPING-START BLOCK-ENTRY }
# indentless_sequence: { ENTRY }
# flow_collection: { FLOW-SEQUENCE-START FLOW-MAPPING-START }
# flow_sequence: { FLOW-SEQUENCE-START }
# flow_mapping: { FLOW-MAPPING-START }
# flow_sequence_entry: { ALIAS ANCHOR TAG SCALAR FLOW-SEQUENCE-START FLOW-MAPPING-START KEY }
# flow_mapping_entry: { ALIAS ANCHOR TAG SCALAR FLOW-SEQUENCE-START FLOW-MAPPING-START KEY }

__all__ = ['NxParser']

from yaml.parser import ParserError

from .scanner import *


class NxParser:
    # Since writing a recursive-descendant parser is a straightforward task, we
    # do not give many comments here.

    DEFAULT_TAGS = {
        '!':   '!',
        '!!':  'tag:yaml.org,2002:',
    }

    def __init__(self):
        self.current_event = None
        self.yaml_version = None
        self.tag_handles = {}
        self.states = []
        self.marks = []
        self.state = self.parse_stream_start

    def dispose(self):
        # Reset the state attributes (to clear self-references)
        self.states = []
        self.state = None

    def check_event(self, *choices):
        # Check the type of the next event.
        if self.current_event is None:
            if self.state:
                self.current_event = self.state()
        if self.current_event is not None:
            if not choices:
                return True
            for choice in choices:
                if isinstance(self.current_event, choice):
                    return True
        return False

    def peek_event(self):
        # Get the next event.
        if self.current_event is None:
            if self.state:
                self.current_event = self.state()
        return self.current_event

    def get_event(self):
        # Get the next event and proceed further.
        if self.current_event is None:
            if self.state:
                self.current_event = self.state()
        value = self.current_event
        self.current_event = None
        return value

    # stream    ::= STREAM-START implicit_document? explicit_document* STREAM-END
    # implicit_document ::= block_node DOCUMENT-END*
    # explicit_document ::= DIRECTIVE* DOCUMENT-START block_node? DOCUMENT-END*

    def parse_stream_start(self):

        # Parse the stream start.
        token = self.get_token()
        (_, start_mark, end_mark, encoding) = token
        event = ("StreamStartEvent", start_mark, end_mark, encoding)

        # Prepare the next state.
        self.state = self.parse_implicit_document_start

        return event

    def parse_implicit_document_start(self):

        # Parse an implicit document.
        if not self.check_token('<directive>', '<document start>',
                '<stream end>'):
            self.tag_handles = self.DEFAULT_TAGS
            token = self.peek_token()
            event = ("DocumentStartEvent", token[1], token[2],
                    False)

            # Prepare the next state.
            self.states.append(self.parse_document_end)
            self.state = self.parse_block_node

            return event

        else:
            return self.parse_document_start()

    def parse_document_start(self):

        # Parse any extra document end indicators.
        while self.check_token('<document end>'):
            self.get_token()

        # Parse an explicit document.
        if not self.check_token('<stream end>'):
            token = self.peek_token()
            start_mark = token[1]
            version, tags = self.process_directives()
            if not self.check_token('<document start>'):
                raise ParserError(None, None,
                        "expected '<document start>', but found %r"
                        % self.peek_token().id,
                        self.peek_token()[1])
            token = self.get_token()
            end_mark = token[2]
            event = ("DocumentStartEvent", start_mark, end_mark,
                    True, version, tags)
            self.states.append(self.parse_document_end)
            self.state = self.parse_document_content
        else:
            # Parse the end of the stream.
            token = self.get_token()
            event = ("StreamEndEvent", token[1], token[2])
            assert not self.states
            assert not self.marks
            self.state = None
        return event

    def parse_document_end(self):

        # Parse the document end.
        token = self.peek_token()
        start_mark = end_mark = token[1]
        explicit = False
        if self.check_token('<document end>'):
            token = self.get_token()
            end_mark = token[2]
            explicit = True
        event = ("DocumentEndEvent", start_mark, end_mark,
                explicit)

        # Prepare the next state.
        self.state = self.parse_document_start

        return event

    def parse_document_content(self):
        if self.check_token('<directive>',
                '<document start>', '<document end>', '<stream end>'):
            event = self.process_empty_scalar(self.peek_token()[1])
            self.state = self.states.pop()
            return event
        else:
            return self.parse_block_node()

    def process_directives(self):
        self.yaml_version = None
        self.tag_handles = {}
        while self.check_token('<directive>'):
            token = self.get_token()
            if token.name == 'YAML':
                if self.yaml_version is not None:
                    raise ParserError(None, None,
                            "found duplicate YAML directive", token[1])
                major, minor = token[2]
                if major != 1:
                    raise ParserError(None, None,
                            "found incompatible YAML document (version 1.* is required)",
                            token[1])
                self.yaml_version = token[2]
            elif token.name == 'TAG':
                handle, prefix = token[2]
                if handle in self.tag_handles:
                    raise ParserError(None, None,
                            "duplicate tag handle %r" % handle,
                            token[1])
                self.tag_handles[handle] = prefix
        if self.tag_handles:
            value = self.yaml_version, self.tag_handles.copy()
        else:
            value = self.yaml_version, None
        for key in self.DEFAULT_TAGS:
            if key not in self.tag_handles:
                self.tag_handles[key] = self.DEFAULT_TAGS[key]
        return value

    # block_node_or_indentless_sequence ::= ALIAS
    #               | properties (block_content | indentless_block_sequence)?
    #               | block_content
    #               | indentless_block_sequence
    # block_node    ::= ALIAS
    #                   | properties block_content?
    #                   | block_content
    # flow_node     ::= ALIAS
    #                   | properties flow_content?
    #                   | flow_content
    # properties    ::= TAG ANCHOR? | ANCHOR TAG?
    # block_content     ::= block_collection | flow_collection | SCALAR
    # flow_content      ::= flow_collection | SCALAR
    # block_collection  ::= block_sequence | block_mapping
    # flow_collection   ::= flow_sequence | flow_mapping

    def parse_block_node(self):
        return self.parse_node(block=True)

    def parse_flow_node(self):
        return self.parse_node()

    def parse_block_node_or_indentless_sequence(self):
        return self.parse_node(block=True, indentless_sequence=True)

    def parse_node(self, block=False, indentless_sequence=False):
        if self.check_token('<alias>'):
            token = self.get_token()
            event = ("AliasEvent", token[2], token[1], token[2])
            self.state = self.states.pop()
        else:
            anchor = None
            tag = None
            start_mark = end_mark = tag_mark = None
            if self.check_token('<anchor>'):
                token = self.get_token()
                start_mark = token[1]
                end_mark = token[2]
                anchor = token[2]
                if self.check_token('<tag>'):
                    token = self.get_token()
                    tag_mark = token[1]
                    end_mark = token[2]
                    tag = token[2]
            elif self.check_token('<tag>'):
                token = self.get_token()
                start_mark = tag_mark = token[1]
                end_mark = token[2]
                tag = token[2]
                if self.check_token('<anchor>'):
                    token = self.get_token()
                    end_mark = token[2]
                    anchor = token[2]
            if tag is not None:
                handle, suffix = tag
                if handle is not None:
                    if handle not in self.tag_handles:
                        raise ParserError("while parsing a node", start_mark,
                                "found undefined tag handle %r" % handle,
                                tag_mark)
                    tag = self.tag_handles[handle]+suffix
                else:
                    tag = suffix
            #if tag == '!':
            #    raise ParserError("while parsing a node", start_mark,
            #            "found non-specific tag '!'", tag_mark,
            #            "Please check 'http://pyyaml.org/wiki/YAMLNonSpecificTag' and share your opinion.")
            if start_mark is None:
                start_mark = end_mark = self.peek_token()[1]
            event = None
            implicit = (tag is None or tag == '!')
            if indentless_sequence and self.check_token('-'):
                end_mark = self.peek_token()[2]
                event = ("SequenceStartEvent", start_mark, end_mark, anchor, tag, implicit, False)
                self.state = self.parse_indentless_sequence_entry
            else:
                if self.check_token('<scalar>'):
                    token = self.get_token()
                    end_mark = token[2]
                    if (token[3] and tag is None) or tag == '!':
                        implicit = (True, False)
                    elif tag is None:
                        implicit = (False, True)
                    else:
                        implicit = (False, False)
                    event = ("ScalarEvent", start_mark, end_mark, anchor, tag, implicit, token[2], token[5])
                    self.state = self.states.pop()
                elif self.check_token('['):
                    end_mark = self.peek_token()[2]
                    event = ("SequenceStartEvent", start_mark, end_mark, anchor, tag, implicit, True)
                    self.state = self.parse_flow_sequence_first_entry
                elif self.check_token('{'):
                    end_mark = self.peek_token()[2]
                    event = ("MappingStartEvent", start_mark, end_mark, anchor, tag, implicit, True)
                    self.state = self.parse_flow_mapping_first_key
                elif block and self.check_token('<block sequence start>'):
                    end_mark = self.peek_token()[1]
                    event = ("SequenceStartEvent", start_mark, end_mark, anchor, tag, implicit, False)
                    self.state = self.parse_block_sequence_first_entry
                elif block and self.check_token('<block mapping start>'):
                    end_mark = self.peek_token()[1]
                    event = ("MappingStartEvent", start_mark, end_mark, anchor, tag, implicit, False)
                    self.state = self.parse_block_mapping_first_key
                # TODO this check wasn't here
                # elif self.check_token('<stream end>'):
                #     pass
                elif anchor is not None or tag is not None:
                    # Empty scalars are allowed even if a tag or an anchor is
                    # specified.
                    event = ("ScalarEvent", start_mark, end_mark, anchor, tag, implicit, '')
                    self.state = self.states.pop()
                else:
                    if block:
                        node = 'block'
                    else:
                        node = 'flow'
                    token = self.peek_token()
                    raise ParserError("while parsing a %s node" % node, None,
                            "expected the node content, but found %s" % token[0],
                            None)
        return event

    # block_sequence ::= BLOCK-SEQUENCE-START (BLOCK-ENTRY block_node?)* BLOCK-END

    def parse_block_sequence_first_entry(self):
        token = self.get_token()
        self.marks.append(token[1])
        return self.parse_block_sequence_entry()

    def parse_block_sequence_entry(self):
        if self.check_token('-'):
            token = self.get_token()
            if not self.check_token('-', '<block end>'):
                self.states.append(self.parse_block_sequence_entry)
                return self.parse_block_node()
            else:
                self.state = self.parse_block_sequence_entry
                return self.process_empty_scalar(token[2])
        if not self.check_token('<block end>'):
            token = self.peek_token()
            raise ParserError("while parsing a block collection", self.marks[-1],
                    "expected <block end>, but found %r" % token[0], token[1])
        token = self.get_token()
        event = ("SequenceEndEvent", token[1], token[2])
        self.state = self.states.pop()
        self.marks.pop()
        return event

    # indentless_sequence ::= (BLOCK-ENTRY block_node?)+

    def parse_indentless_sequence_entry(self):
        if self.check_token('-'):
            token = self.get_token()
            if not self.check_token('-',
                    '?', ':', '<block end>'):
                self.states.append(self.parse_indentless_sequence_entry)
                return self.parse_block_node()
            else:
                self.state = self.parse_indentless_sequence_entry
                return self.process_empty_scalar(token[2])
        token = self.peek_token()
        event = ("SequenceEndEvent", token[1], token[1])
        self.state = self.states.pop()
        return event

    # block_mapping     ::= BLOCK-MAPPING_START
    #                       ((KEY block_node_or_indentless_sequence?)?
    #                       (VALUE block_node_or_indentless_sequence?)?)*
    #                       BLOCK-END

    def parse_block_mapping_first_key(self):
        token = self.get_token()
        self.marks.append(token[1])
        return self.parse_block_mapping_key()

    def parse_block_mapping_key(self):
        if self.check_token('?'):
            token = self.get_token()
            if not self.check_token('?', ':', '<block end>'):
                self.states.append(self.parse_block_mapping_value)
                return self.parse_block_node_or_indentless_sequence()
            else:
                self.state = self.parse_block_mapping_value
                return self.process_empty_scalar(token[2])
        if not self.check_token('<block end>'):
            token = self.peek_token()
            raise ParserError("while parsing a block mapping", self.marks[-1],
                    "expected <block end>, but found %r" % token[0], token[1])
        token = self.get_token()
        event = ("MappingEndEvent", token[1], token[2])
        self.state = self.states.pop()
        self.marks.pop()
        return event

    def parse_block_mapping_value(self):
        if self.check_token(':'):
            token = self.get_token()
            if not self.check_token('?', ':', '<block end>'):
                self.states.append(self.parse_block_mapping_key)
                return self.parse_block_node_or_indentless_sequence()
            else:
                self.state = self.parse_block_mapping_key
                return self.process_empty_scalar(token[2])
        else:
            self.state = self.parse_block_mapping_key
            token = self.peek_token()
            return self.process_empty_scalar(token[1])

    # flow_sequence     ::= FLOW-SEQUENCE-START
    #                       (flow_sequence_entry FLOW-ENTRY)*
    #                       flow_sequence_entry?
    #                       FLOW-SEQUENCE-END
    # flow_sequence_entry   ::= flow_node | KEY flow_node? (VALUE flow_node?)?
    #
    # Note that while production rules for both flow_sequence_entry and
    # flow_mapping_entry are equal, their interpretations are different.
    # For `flow_sequence_entry`, the part `KEY flow_node? (VALUE flow_node?)?`
    # generate an inline mapping (set syntax).

    def parse_flow_sequence_first_entry(self):
        token = self.get_token()
        self.marks.append(token[1])
        return self.parse_flow_sequence_entry(first=True)

    def parse_flow_sequence_entry(self, first=False):
        if not self.check_token(']'):
            if not first:
                if self.check_token(','):
                    self.get_token()
                else:
                    token = self.peek_token()
                    raise ParserError("while parsing a flow sequence", self.marks[-1],
                            "expected ',' or ']', but got %r" % token[0], token[1])
            
            if self.check_token('?'):
                token = self.peek_token()
                event = ("MappingStartEvent", None, None, True,
                        token[1], token[2],
                        True)
                self.state = self.parse_flow_sequence_entry_mapping_key
                return event
            elif not self.check_token(']'):
                self.states.append(self.parse_flow_sequence_entry)
                return self.parse_flow_node()
        token = self.get_token()
        event = ("SequenceEndEvent", token[1], token[2])
        self.state = self.states.pop()
        self.marks.pop()
        return event

    def parse_flow_sequence_entry_mapping_key(self):
        token = self.get_token()
        if not self.check_token(':',
                ',', ']'):
            self.states.append(self.parse_flow_sequence_entry_mapping_value)
            return self.parse_flow_node()
        else:
            self.state = self.parse_flow_sequence_entry_mapping_value
            return self.process_empty_scalar(token[2])

    def parse_flow_sequence_entry_mapping_value(self):
        if self.check_token(':'):
            token = self.get_token()
            if not self.check_token(',', ']'):
                self.states.append(self.parse_flow_sequence_entry_mapping_end)
                return self.parse_flow_node()
            else:
                self.state = self.parse_flow_sequence_entry_mapping_end
                return self.process_empty_scalar(token[2])
        else:
            self.state = self.parse_flow_sequence_entry_mapping_end
            token = self.peek_token()
            return self.process_empty_scalar(token[1])

    def parse_flow_sequence_entry_mapping_end(self):
        self.state = self.parse_flow_sequence_entry
        token = self.peek_token()
        return ("MappingEndEvent", token[1], token[1])

    # flow_mapping  ::= FLOW-MAPPING-START
    #                   (flow_mapping_entry FLOW-ENTRY)*
    #                   flow_mapping_entry?
    #                   FLOW-MAPPING-END
    # flow_mapping_entry    ::= flow_node | KEY flow_node? (VALUE flow_node?)?

    def parse_flow_mapping_first_key(self):
        token = self.get_token()
        self.marks.append(token[1])
        return self.parse_flow_mapping_key(first=True)

    def parse_flow_mapping_key(self, first=False):
        if not self.check_token('}'):
            if not first:
                if self.check_token(','):
                    self.get_token()
                else:
                    token = self.peek_token()
                    raise ParserError("while parsing a flow mapping", self.marks[-1],
                            "expected ',' or '}', but got %r" % token[0], token[1])
            if self.check_token('?'):
                token = self.get_token()
                if not self.check_token(':',
                        ',', '}'):
                    self.states.append(self.parse_flow_mapping_value)
                    return self.parse_flow_node()
                else:
                    self.state = self.parse_flow_mapping_value
                    return self.process_empty_scalar(token[2])
            elif not self.check_token('}'):
                self.states.append(self.parse_flow_mapping_empty_value)
                return self.parse_flow_node()
        token = self.get_token()
        event = ("MappingEndEvent", token[1], token[2])
        self.state = self.states.pop()
        self.marks.pop()
        return event

    def parse_flow_mapping_value(self):
        if self.check_token(':'):
            token = self.get_token()
            if not self.check_token(',', '}'):
                self.states.append(self.parse_flow_mapping_key)
                return self.parse_flow_node()
            else:
                self.state = self.parse_flow_mapping_key
                return self.process_empty_scalar(token[2])
        else:
            self.state = self.parse_flow_mapping_key
            token = self.peek_token()
            return self.process_empty_scalar(token[1])

    def parse_flow_mapping_empty_value(self):
        self.state = self.parse_flow_mapping_key
        return self.process_empty_scalar(self.peek_token()[1])

    def process_empty_scalar(self, mark):
        return ("ScalarEvent", mark, mark, None, None, True, False, '')

