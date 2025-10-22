
# Scanner produces tokens of the following types:
# STREAM-START
# STREAM-END
# DIRECTIVE(name, value)
# DOCUMENT-START
# DOCUMENT-END
# BLOCK-SEQUENCE-START
# BLOCK-MAPPING-START
# BLOCK-END
# FLOW-SEQUENCE-START
# FLOW-MAPPING-START
# FLOW-SEQUENCE-END
# FLOW-MAPPING-END
# BLOCK-ENTRY
# FLOW-ENTRY
# KEY
# VALUE
# ALIAS(value)
# ANCHOR(value)
# TAG(value)
# SCALAR(value, plain, style)
#
# Read comments in the Scanner code for more details.
#

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


__all__ = ['NxScanner']

import networkx as nx
from .nx_hif.hif import *
from yaml.composer import ComposerError
from yaml.parser import ParserError
from yaml.scanner import SimpleKey, ScannerError


class NxScanner:

    DEFAULT_TAGS = {
        '!':   '!',
        '!!':  'tag:yaml.org,2002:',
    }

    def __init__(self):
        """Initialize the scanner."""
        # It is assumed that Scanner and Reader will have a common descendant.
        # Reader do the dirty work of checking for BOM and converting the
        # input data to Unicode. It also adds NUL to the end.
        #
        # Reader supports the following methods
        #   self.peek(i=0)       # peek the next i-th character
        #   self.prefix(l=1)     # peek the next l characters
        #   self.forward(l=1)    # read the next l characters and move the pointer.

        # Had we reached the end of the stream?
        self.done = False

        # The number of unclosed '{' and '['. `flow_level == 0` means block
        # context.
        self.flow_level = 0

        # List of processed tokens that are not yet emitted.
        self.tokens = []

        # Add the STREAM-START token.
        self.fetch_stream_start()

        # Number of tokens that were emitted through the `get_token` method.
        self.tokens_taken = 0

        # The current indentation level.
        self.indent = -1

        # Past indentation levels.
        self.indents = []

        # Variables related to simple keys treatment.

        # A simple key is a key that is not denoted by the '?' indicator.
        # Example of simple keys:
        #   ---
        #   block simple key: value
        #   ? not a simple key:
        #   : { flow simple key: value }
        # We emit the KEY token before all keys, so when we find a potential
        # simple key, we try to locate the corresponding ':' indicator.
        # Simple keys should be limited to a single line and 1024 characters.

        # Can a simple key start at the current position? A simple key may
        # start:
        # - at the beginning of the line, not counting indentation spaces
        #       (in block context),
        # - after '{', '[', ',' (in the flow context),
        # - after '?', ':', '-' (in the block context).
        # In the block context, this flag also signifies if a block collection
        # may start at the current position.
        self.allow_simple_key = True

        # Keep track of possible simple keys. This is a dictionary. The key
        # is `flow_level`; there can be no more that one possible simple key
        # for each level. The value is a SimpleKey record:
        #   (token_number, required, index, line, column, mark)
        # A simple key may start with ALIAS, ANCHOR, TAG, SCALAR(flow),
        # '[', or '{' tokens.
        self.possible_simple_keys = {}

        # Parser
        self.current_event = None
        self.yaml_version = None
        self.tag_handles = {}
        self.states = []
        self.marks = []
        self.state = self.parse_stream_start

        # Composer
        self.anchors = {}

    def dispose(self):
        # Reset the state attributes (to clear self-references)
        self.states = []
        self.state = None

    # Public methods.

    def check_token(self, *choices):
        # Check if the next token is one of the given types.
        while self.need_more_tokens():
            self.fetch_more_tokens()
        if self.tokens:
            if not choices:
                return True
            for choice in choices:
                if self.tokens[0][0] == choice:
                    return True
        return False

    def peek_token(self):
        # Return the next token, but do not delete if from the queue.
        # Return None if no more tokens.
        while self.need_more_tokens():
            self.fetch_more_tokens()
        if self.tokens:
            return self.tokens[0]
        else:
            return None

    def get_token(self):
        # Return the next token.
        while self.need_more_tokens():
            self.fetch_more_tokens()
        if self.tokens:
            self.tokens_taken += 1
            return self.tokens.pop(0)

    # Private methods.

    def need_more_tokens(self):
        if self.done:
            return False
        if not self.tokens:
            return True
        # The current token may be a potential simple key, so we
        # need to look further.
        self.stale_possible_simple_keys()
        if self.next_possible_simple_key() == self.tokens_taken:
            return True

    def fetch_more_tokens(self):

        # Eat whitespaces and comments until we reach the next token.
        self.scan_to_next_token()

        # Remove obsolete possible simple keys.
        self.stale_possible_simple_keys()

        # Compare the current indentation and column. It may add some tokens
        # and decrease the current indentation level.
        self.unwind_indent(self.column)

        # Peek the next character.
        ch = self.peek()

        # Is it the end of stream?
        if ch == '\0':
            return self.fetch_stream_end()

        # Is it a directive?
        if ch == '%' and self.check_directive():
            return self.fetch_directive()

        # Is it the document start?
        if ch == '-' and self.check_document_start():
            return self.fetch_document_start()

        # Is it the document end?
        if ch == '.' and self.check_document_end():
            return self.fetch_document_end()

        # TODO: support for BOM within a stream.
        #if ch == '\uFEFF':
        #    return self.fetch_bom()    <-- issue BOMToken

        # Note: the order of the following checks is NOT significant.

        # Is it the flow sequence start indicator?
        if ch == '[':
            return self.fetch_flow_sequence_start()

        # Is it the flow mapping start indicator?
        if ch == '{':
            return self.fetch_flow_mapping_start()

        # Is it the flow sequence end indicator?
        if ch == ']':
            return self.fetch_flow_sequence_end()

        # Is it the flow mapping end indicator?
        if ch == '}':
            return self.fetch_flow_mapping_end()

        # Is it the flow entry indicator?
        if ch == ',':
            return self.fetch_flow_entry()

        # Is it the block entry indicator?
        if ch == '-' and self.check_block_entry():
            return self.fetch_block_entry()

        # Is it the key indicator?
        if ch == '?' and self.check_key():
            return self.fetch_key()

        # Is it the value indicator?
        if ch == ':' and self.check_value():
            return self.fetch_value()

        # Is it an alias?
        if ch == '*':
            return self.fetch_alias()

        # Is it an anchor?
        if ch == '&':
            return self.fetch_anchor()

        # Is it a tag?
        if ch == '!':
            return self.fetch_tag()

        # Is it a literal scalar?
        if ch == '|' and not self.flow_level:
            return self.fetch_literal()

        # Is it a folded scalar?
        if ch == '>' and not self.flow_level:
            return self.fetch_folded()

        # Is it a single quoted scalar?
        if ch == '\'':
            return self.fetch_single()

        # Is it a double quoted scalar?
        if ch == '\"':
            return self.fetch_double()

        # It must be a plain scalar then.
        if self.check_plain():
            return self.fetch_plain()

        # No? It's an error. Let's produce a nice error message.
        raise ScannerError("while scanning for the next token", None,
                "found character %r that cannot start any token" % ch,
                self.get_mark())

    # Simple keys treatment.

    def next_possible_simple_key(self):
        # Return the number of the nearest possible simple key. Actually we
        # don't need to loop through the whole dictionary. We may replace it
        # with the following code:
        #   if not self.possible_simple_keys:
        #       return None
        #   return self.possible_simple_keys[
        #           min(self.possible_simple_keys.keys())].token_number
        min_token_number = None
        for level in self.possible_simple_keys:
            key = self.possible_simple_keys[level]
            if min_token_number is None or key.token_number < min_token_number:
                min_token_number = key.token_number
        return min_token_number

    def stale_possible_simple_keys(self):
        # Remove entries that are no longer possible simple keys. According to
        # the YAML specification, simple keys
        # - should be limited to a single line,
        # - should be no longer than 1024 characters.
        # Disabling this procedure will allow simple keys of any length and
        # height (may cause problems if indentation is broken though).
        for level in list(self.possible_simple_keys):
            key = self.possible_simple_keys[level]
            if key.line != self.line  \
                    or self.index-key.index > 1024:
                if key.required:
                    raise ScannerError("while scanning a simple key", key.mark,
                            "could not find expected ':'", self.get_mark())
                del self.possible_simple_keys[level]

    def save_possible_simple_key(self):
        # The next token may start a simple key. We check if it's possible
        # and save its position. This function is called for
        #   ALIAS, ANCHOR, TAG, SCALAR(flow), '[', and '{'.

        # Check if a simple key is required at the current position.
        required = not self.flow_level and self.indent == self.column

        # The next token might be a simple key. Let's save it's number and
        # position.
        if self.allow_simple_key:
            self.remove_possible_simple_key()
            token_number = self.tokens_taken+len(self.tokens)
            key = SimpleKey(token_number, required,
                    self.index, self.line, self.column, self.get_mark())
            self.possible_simple_keys[self.flow_level] = key

    def remove_possible_simple_key(self):
        # Remove the saved possible key position at the current flow level.
        if self.flow_level in self.possible_simple_keys:
            key = self.possible_simple_keys[self.flow_level]
            
            if key.required:
                raise ScannerError("while scanning a simple key", key.mark,
                        "could not find expected ':'", self.get_mark())

            del self.possible_simple_keys[self.flow_level]

    # Indentation functions.

    def unwind_indent(self, column):

        ## In flow context, tokens should respect indentation.
        ## Actually the condition should be `self.indent >= column` according to
        ## the spec. But this condition will prohibit intuitively correct
        ## constructions such as
        ## key : {
        ## }
        #if self.flow_level and self.indent > column:
        #    raise ScannerError(None, None,
        #            "invalid indentation or unclosed '[' or '{'",
        #            self.get_mark())

        # In the flow context, indentation is ignored. We make the scanner less
        # restrictive then specification requires.
        if self.flow_level:
            return

        # In block context, we may need to issue the BLOCK-END tokens.
        while self.indent > column:
            mark = self.get_mark()
            self.indent = self.indents.pop()
            self.tokens.append(('<block end>', mark, mark))

    def add_indent(self, column):
        # Check if we need to increase indentation.
        if self.indent < column:
            self.indents.append(self.indent)
            self.indent = column
            return True
        return False

    # Fetchers.

    def fetch_stream_start(self):
        # We always add STREAM-START as the first token and STREAM-END as the
        # last token.

        # Read the token.
        mark = self.get_mark()
        
        # Add STREAM-START.
        self.tokens.append(('<stream start>', mark, mark,
            self.encoding))
        

    def fetch_stream_end(self):

        # Set the current indentation to -1.
        self.unwind_indent(-1)

        # Reset simple keys.
        self.remove_possible_simple_key()
        self.allow_simple_key = False
        self.possible_simple_keys = {}

        # Read the token.
        mark = self.get_mark()
        
        # Add STREAM-END.
        self.tokens.append(('<stream end>', mark, mark))

        # The steam is finished.
        self.done = True

    def fetch_directive(self):
        
        # Set the current indentation to -1.
        self.unwind_indent(-1)

        # Reset simple keys.
        self.remove_possible_simple_key()
        self.allow_simple_key = False

        # Scan and add DIRECTIVE.
        self.tokens.append(self.scan_directive())

    def fetch_document_start(self):
        self.fetch_document_indicator('<document start>')

    def fetch_document_end(self):
        self.fetch_document_indicator('<document end>')

    def fetch_document_indicator(self, TokenClass):

        # Set the current indentation to -1.
        self.unwind_indent(-1)

        # Reset simple keys. Note that there could not be a block collection
        # after '---'.
        self.remove_possible_simple_key()
        self.allow_simple_key = False

        # Add DOCUMENT-START or DOCUMENT-END.
        start_mark = self.get_mark()
        self.forward(3)
        end_mark = self.get_mark()
        self.tokens.append((TokenClass, start_mark, end_mark))

    def fetch_flow_sequence_start(self):
        self.fetch_flow_collection_start('[')

    def fetch_flow_mapping_start(self):
        self.fetch_flow_collection_start('{')

    def fetch_flow_collection_start(self, TokenClass):

        # '[' and '{' may start a simple key.
        self.save_possible_simple_key()

        # Increase the flow level.
        self.flow_level += 1

        # Simple keys are allowed after '[' and '{'.
        self.allow_simple_key = True

        # Add FLOW-SEQUENCE-START or FLOW-MAPPING-START.
        start_mark = self.get_mark()
        self.forward()
        end_mark = self.get_mark()
        self.tokens.append((TokenClass, start_mark, end_mark))

    def fetch_flow_sequence_end(self):
        self.fetch_flow_collection_end(']')

    def fetch_flow_mapping_end(self):
        self.fetch_flow_collection_end('}')

    def fetch_flow_collection_end(self, TokenClass):

        # Reset possible simple key on the current level.
        self.remove_possible_simple_key()

        # Decrease the flow level.
        self.flow_level -= 1

        # No simple keys after ']' or '}'.
        self.allow_simple_key = False

        # Add FLOW-SEQUENCE-END or FLOW-MAPPING-END.
        start_mark = self.get_mark()
        self.forward()
        end_mark = self.get_mark()
        self.tokens.append((TokenClass, start_mark, end_mark))

    def fetch_flow_entry(self):

        # Simple keys are allowed after ','.
        self.allow_simple_key = True

        # Reset possible simple key on the current level.
        self.remove_possible_simple_key()

        # Add FLOW-ENTRY.
        start_mark = self.get_mark()
        self.forward()
        end_mark = self.get_mark()
        self.tokens.append((",", start_mark, end_mark))

    def fetch_block_entry(self):

        # Block context needs additional checks.
        if not self.flow_level:

            # Are we allowed to start a new entry?
            if not self.allow_simple_key:
                raise ScannerError(None, None,
                        "sequence entries are not allowed here",
                        self.get_mark())

            # We may need to add BLOCK-SEQUENCE-START.
            if self.add_indent(self.column):
                mark = self.get_mark()
                self.tokens.append(('<block sequence start>', mark, mark))

        # It's an error for the block entry to occur in the flow context,
        # but we let the parser detect this.
        else:
            pass

        # Simple keys are allowed after '-'.
        self.allow_simple_key = True

        # Reset possible simple key on the current level.
        self.remove_possible_simple_key()

        # Add BLOCK-ENTRY.
        start_mark = self.get_mark()
        self.forward()
        end_mark = self.get_mark()
        self.tokens.append(("-", start_mark, end_mark))

    def fetch_key(self):
        
        # Block context needs additional checks.
        if not self.flow_level:

            # Are we allowed to start a key (not necessary a simple)?
            if not self.allow_simple_key:
                raise ScannerError(None, None,
                        "mapping keys are not allowed here",
                        self.get_mark())

            # We may need to add BLOCK-MAPPING-START.
            if self.add_indent(self.column):
                mark = self.get_mark()
                self.tokens.append(('<block mapping start>', mark, mark))

        # Simple keys are allowed after '?' in the block context.
        self.allow_simple_key = not self.flow_level

        # Reset possible simple key on the current level.
        self.remove_possible_simple_key()

        # Add KEY.
        start_mark = self.get_mark()
        self.forward()
        end_mark = self.get_mark()
        self.tokens.append(("?", start_mark, end_mark))

    def fetch_value(self):

        # Do we determine a simple key?
        if self.flow_level in self.possible_simple_keys:

            # Add KEY.
            key = self.possible_simple_keys[self.flow_level]
            del self.possible_simple_keys[self.flow_level]
            self.tokens.insert(key.token_number-self.tokens_taken,
                    ('?', key.mark, key.mark))

            # If this key starts a new block mapping, we need to add
            # BLOCK-MAPPING-START.
            if not self.flow_level:
                if self.add_indent(key.column):
                    self.tokens.insert(key.token_number-self.tokens_taken,
                            ('<block mapping start>', key.mark, key.mark))

            # There cannot be two simple keys one after another.
            self.allow_simple_key = False

        # It must be a part of a complex key.
        else:
            
            # Block context needs additional checks.
            # (Do we really need them? They will be caught by the parser
            # anyway.)
            if not self.flow_level:

                # We are allowed to start a complex value if and only if
                # we can start a simple key.
                if not self.allow_simple_key:
                    raise ScannerError(None, None,
                            "mapping values are not allowed here",
                            self.get_mark())

            # If this value starts a new block mapping, we need to add
            # BLOCK-MAPPING-START.  It will be detected as an error later by
            # the parser.
            if not self.flow_level:
                if self.add_indent(self.column):
                    mark = self.get_mark()
                    self.tokens.append(('<block mapping start>', mark, mark))

            # Simple keys are allowed after ':' in the block context.
            self.allow_simple_key = not self.flow_level

            # Reset possible simple key on the current level.
            self.remove_possible_simple_key()

        # Add VALUE.
        start_mark = self.get_mark()
        self.forward()
        end_mark = self.get_mark()
        self.tokens.append((":", start_mark, end_mark))

    def fetch_alias(self):

        # ALIAS could be a simple key.
        self.save_possible_simple_key()

        # No simple keys after ALIAS.
        self.allow_simple_key = False

        # Scan and add ALIAS.
        self.tokens.append(self.scan_anchor('<alias>'))

    def fetch_anchor(self):

        # ANCHOR could start a simple key.
        self.save_possible_simple_key()

        # No simple keys after ANCHOR.
        self.allow_simple_key = False

        # Scan and add ANCHOR.
        self.tokens.append(self.scan_anchor('<anchor>'))

    def fetch_tag(self):

        # TAG could start a simple key.
        self.save_possible_simple_key()

        # No simple keys after TAG.
        self.allow_simple_key = False

        # Scan and add TAG.
        self.tokens.append(self.scan_tag())

    def fetch_literal(self):
        self.fetch_block_scalar(style='|')

    def fetch_folded(self):
        self.fetch_block_scalar(style='>')

    def fetch_block_scalar(self, style):

        # A simple key may follow a block scalar.
        self.allow_simple_key = True

        # Reset possible simple key on the current level.
        self.remove_possible_simple_key()

        # Scan and add SCALAR.
        self.tokens.append(self.scan_block_scalar(style))

    def fetch_single(self):
        self.fetch_flow_scalar(style='\'')

    def fetch_double(self):
        self.fetch_flow_scalar(style='"')

    def fetch_flow_scalar(self, style):

        # A flow scalar could be a simple key.
        self.save_possible_simple_key()

        # No simple keys after flow scalars.
        self.allow_simple_key = False

        # Scan and add SCALAR.
        self.tokens.append(self.scan_flow_scalar(style))

    def fetch_plain(self):

        # A plain scalar could be a simple key.
        self.save_possible_simple_key()

        # No simple keys after plain scalars. But note that `scan_plain` will
        # change this flag if the scan is finished at the beginning of the
        # line.
        self.allow_simple_key = False

        # Scan and add SCALAR. May change `allow_simple_key`.
        self.tokens.append(self.scan_plain())

    # Checkers.

    def check_directive(self):

        # DIRECTIVE:        ^ '%' ...
        # The '%' indicator is already checked.
        if self.column == 0:
            return True

    def check_document_start(self):

        # DOCUMENT-START:   ^ '---' (' '|'\n')
        if self.column == 0:
            if self.prefix(3) == '---'  \
                    and self.peek(3) in '\0 \t\r\n\x85\u2028\u2029':
                return True

    def check_document_end(self):

        # DOCUMENT-END:     ^ '...' (' '|'\n')
        if self.column == 0:
            if self.prefix(3) == '...'  \
                    and self.peek(3) in '\0 \t\r\n\x85\u2028\u2029':
                return True

    def check_block_entry(self):

        # BLOCK-ENTRY:      '-' (' '|'\n')
        return self.peek(1) in '\0 \t\r\n\x85\u2028\u2029'

    def check_key(self):

        # KEY(flow context):    '?'
        if self.flow_level:
            return True

        # KEY(block context):   '?' (' '|'\n')
        else:
            return self.peek(1) in '\0 \t\r\n\x85\u2028\u2029'

    def check_value(self):

        # VALUE(flow context):  ':'
        if self.flow_level:
            return True

        # VALUE(block context): ':' (' '|'\n')
        else:
            return self.peek(1) in '\0 \t\r\n\x85\u2028\u2029'

    def check_plain(self):

        # A plain scalar may start with any non-space character except:
        #   '-', '?', ':', ',', '[', ']', '{', '}',
        #   '#', '&', '*', '!', '|', '>', '\'', '\"',
        #   '%', '@', '`'.
        #
        # It may also start with
        #   '-', '?', ':'
        # if it is followed by a non-space character.
        #
        # Note that we limit the last rule to the block context (except the
        # '-' character) because we want the flow context to be space
        # independent.
        ch = self.peek()
        return ch not in '\0 \t\r\n\x85\u2028\u2029-?:,[]{}#&*!|>\'\"%@`'  \
                or (self.peek(1) not in '\0 \t\r\n\x85\u2028\u2029'
                        and (ch == '-' or (not self.flow_level and ch in '?:')))

    # Scanners.

    def scan_to_next_token(self):
        # We ignore spaces, line breaks and comments.
        # If we find a line break in the block context, we set the flag
        # `allow_simple_key` on.
        # The byte order mark is stripped if it's the first character in the
        # stream. We do not yet support BOM inside the stream as the
        # specification requires. Any such mark will be considered as a part
        # of the document.
        #
        # TODO: We need to make tab handling rules more sane. A good rule is
        #   Tabs cannot precede tokens
        #   BLOCK-SEQUENCE-START, BLOCK-MAPPING-START, BLOCK-END,
        #   KEY(block), VALUE(block), BLOCK-ENTRY
        # So the checking code is
        #   if <TAB>:
        #       self.allow_simple_keys = False
        # We also need to add the check for `allow_simple_keys == True` to
        # `unwind_indent` before issuing BLOCK-END.
        # Scanners for block, flow, and plain scalars need to be modified.

        if self.index == 0 and self.peek() == '\uFEFF':
            self.forward()
        found = False
        while not found:
            while self.peek() == ' ':
                self.forward()
            if self.peek() == '#':
                while self.peek() not in '\0\r\n\x85\u2028\u2029':
                    self.forward()
            if self.scan_line_break():
                if not self.flow_level:
                    self.allow_simple_key = True
            else:
                found = True

    def scan_directive(self):
        # See the specification for details.
        start_mark = self.get_mark()
        self.forward()
        name = self.scan_directive_name(start_mark)
        value = None
        if name == 'YAML':
            value = self.scan_yaml_directive_value(start_mark)
            end_mark = self.get_mark()
        elif name == 'TAG':
            value = self.scan_tag_directive_value(start_mark)
            end_mark = self.get_mark()
        else:
            end_mark = self.get_mark()
            while self.peek() not in '\0\r\n\x85\u2028\u2029':
                self.forward()
        self.scan_directive_ignored_line(start_mark)
        return DirectiveToken(name, value, start_mark, end_mark)

    def scan_directive_name(self, start_mark):
        # See the specification for details.
        length = 0
        ch = self.peek(length)
        while '0' <= ch <= '9' or 'A' <= ch <= 'Z' or 'a' <= ch <= 'z'  \
                or ch in '-_':
            length += 1
            ch = self.peek(length)
        if not length:
            raise ScannerError("while scanning a directive", start_mark,
                    "expected alphabetic or numeric character, but found %r"
                    % ch, self.get_mark())
        value = self.prefix(length)
        self.forward(length)
        ch = self.peek()
        if ch not in '\0 \r\n\x85\u2028\u2029':
            raise ScannerError("while scanning a directive", start_mark,
                    "expected alphabetic or numeric character, but found %r"
                    % ch, self.get_mark())
        return value

    def scan_yaml_directive_value(self, start_mark):
        # See the specification for details.
        while self.peek() == ' ':
            self.forward()
        major = self.scan_yaml_directive_number(start_mark)
        if self.peek() != '.':
            raise ScannerError("while scanning a directive", start_mark,
                    "expected a digit or '.', but found %r" % self.peek(),
                    self.get_mark())
        self.forward()
        minor = self.scan_yaml_directive_number(start_mark)
        if self.peek() not in '\0 \r\n\x85\u2028\u2029':
            raise ScannerError("while scanning a directive", start_mark,
                    "expected a digit or ' ', but found %r" % self.peek(),
                    self.get_mark())
        return (major, minor)

    def scan_yaml_directive_number(self, start_mark):
        # See the specification for details.
        ch = self.peek()
        if not ('0' <= ch <= '9'):
            raise ScannerError("while scanning a directive", start_mark,
                    "expected a digit, but found %r" % ch, self.get_mark())
        length = 0
        while '0' <= self.peek(length) <= '9':
            length += 1
        value = int(self.prefix(length))
        self.forward(length)
        return value

    def scan_tag_directive_value(self, start_mark):
        # See the specification for details.
        while self.peek() == ' ':
            self.forward()
        handle = self.scan_tag_directive_handle(start_mark)
        while self.peek() == ' ':
            self.forward()
        prefix = self.scan_tag_directive_prefix(start_mark)
        return (handle, prefix)

    def scan_tag_directive_handle(self, start_mark):
        # See the specification for details.
        value = self.scan_tag_handle('directive', start_mark)
        ch = self.peek()
        if ch != ' ':
            raise ScannerError("while scanning a directive", start_mark,
                    "expected ' ', but found %r" % ch, self.get_mark())
        return value

    def scan_tag_directive_prefix(self, start_mark):
        # See the specification for details.
        value = self.scan_tag_uri('directive', start_mark)
        ch = self.peek()
        if ch not in '\0 \r\n\x85\u2028\u2029':
            raise ScannerError("while scanning a directive", start_mark,
                    "expected ' ', but found %r" % ch, self.get_mark())
        return value

    def scan_directive_ignored_line(self, start_mark):
        # See the specification for details.
        while self.peek() == ' ':
            self.forward()
        if self.peek() == '#':
            while self.peek() not in '\0\r\n\x85\u2028\u2029':
                self.forward()
        ch = self.peek()
        if ch not in '\0\r\n\x85\u2028\u2029':
            raise ScannerError("while scanning a directive", start_mark,
                    "expected a comment or a line break, but found %r"
                        % ch, self.get_mark())
        self.scan_line_break()

    def scan_anchor(self, TokenClass):
        # The specification does not restrict characters for anchors and
        # aliases. This may lead to problems, for instance, the document:
        #   [ *alias, value ]
        # can be interpreted in two ways, as
        #   [ "value" ]
        # and
        #   [ *alias , "value" ]
        # Therefore we restrict aliases to numbers and ASCII letters.
        start_mark = self.get_mark()
        indicator = self.peek()
        if indicator == '*':
            name = 'alias'
        else:
            name = 'anchor'
        self.forward()
        length = 0
        ch = self.peek(length)
        while '0' <= ch <= '9' or 'A' <= ch <= 'Z' or 'a' <= ch <= 'z'  \
                or ch in '-_':
            length += 1
            ch = self.peek(length)
        if not length:
            raise ScannerError("while scanning an %s" % name, start_mark,
                    "expected alphabetic or numeric character, but found %r"
                    % ch, self.get_mark())
        value = self.prefix(length)
        self.forward(length)
        ch = self.peek()
        if ch not in '\0 \t\r\n\x85\u2028\u2029?:,]}%@`':
            raise ScannerError("while scanning an %s" % name, start_mark,
                    "expected alphabetic or numeric character, but found %r"
                    % ch, self.get_mark())
        end_mark = self.get_mark()
        return (TokenClass, start_mark, end_mark, value)

    def scan_tag(self):
        # See the specification for details.
        start_mark = self.get_mark()
        ch = self.peek(1)
        if ch == '<':
            handle = None
            self.forward(2)
            suffix = self.scan_tag_uri('tag', start_mark)
            if self.peek() != '>':
                raise ScannerError("while parsing a tag", start_mark,
                        "expected '>', but found %r" % self.peek(),
                        self.get_mark())
            self.forward()
        elif ch in '\0 \t\r\n\x85\u2028\u2029':
            handle = None
            suffix = '!'
            self.forward()
        else:
            length = 1
            use_handle = False
            while ch not in '\0 \r\n\x85\u2028\u2029':
                if ch == '!':
                    use_handle = True
                    break
                length += 1
                ch = self.peek(length)
            handle = '!'
            if use_handle:
                handle = self.scan_tag_handle('tag', start_mark)
            else:
                handle = '!'
                self.forward()
            suffix = self.scan_tag_uri('tag', start_mark)
        ch = self.peek()
        if ch not in '\0 \r\n\x85\u2028\u2029':
            raise ScannerError("while scanning a tag", start_mark,
                    "expected ' ', but found %r" % ch, self.get_mark())
        value = (handle, suffix)
        end_mark = self.get_mark()
        return ('<tag>', start_mark, end_mark, value)

    def scan_block_scalar(self, style):
        # See the specification for details.

        if style == '>':
            folded = True
        else:
            folded = False

        chunks = []
        start_mark = self.get_mark()

        # Scan the header.
        self.forward()
        chomping, increment = self.scan_block_scalar_indicators(start_mark)
        self.scan_block_scalar_ignored_line(start_mark)

        # Determine the indentation level and go to the first non-empty line.
        min_indent = self.indent+1
        if min_indent < 1:
            min_indent = 1
        if increment is None:
            breaks, max_indent, end_mark = self.scan_block_scalar_indentation()
            indent = max(min_indent, max_indent)
        else:
            indent = min_indent+increment-1
            breaks, end_mark = self.scan_block_scalar_breaks(indent)
        line_break = ''

        # Scan the inner part of the block scalar.
        while self.column == indent and self.peek() != '\0':
            chunks.extend(breaks)
            leading_non_space = self.peek() not in ' \t'
            length = 0
            while self.peek(length) not in '\0\r\n\x85\u2028\u2029':
                length += 1
            chunks.append(self.prefix(length))
            self.forward(length)
            line_break = self.scan_line_break()
            breaks, end_mark = self.scan_block_scalar_breaks(indent)
            if self.column == indent and self.peek() != '\0':

                # Unfortunately, folding rules are ambiguous.
                #
                # This is the folding according to the specification:
                
                if folded and line_break == '\n'    \
                        and leading_non_space and self.peek() not in ' \t':
                    if not breaks:
                        chunks.append(' ')
                else:
                    chunks.append(line_break)
                
                # This is Clark Evans's interpretation (also in the spec
                # examples):
                #
                #if folded and line_break == '\n':
                #    if not breaks:
                #        if self.peek() not in ' \t':
                #            chunks.append(' ')
                #        else:
                #            chunks.append(line_break)
                #else:
                #    chunks.append(line_break)
            else:
                break

        # Chomp the tail.
        if chomping is not False:
            chunks.append(line_break)
        if chomping is True:
            chunks.extend(breaks)

        # We are done.
        return ('<scalar>', start_mark, end_mark, False, style, ''.join(chunks))

    def scan_block_scalar_indicators(self, start_mark):
        # See the specification for details.
        chomping = None
        increment = None
        ch = self.peek()
        if ch in '+-':
            if ch == '+':
                chomping = True
            else:
                chomping = False
            self.forward()
            ch = self.peek()
            if ch in '0123456789':
                increment = int(ch)
                if increment == 0:
                    raise ScannerError("while scanning a block scalar", start_mark,
                            "expected indentation indicator in the range 1-9, but found 0",
                            self.get_mark())
                self.forward()
        elif ch in '0123456789':
            increment = int(ch)
            if increment == 0:
                raise ScannerError("while scanning a block scalar", start_mark,
                        "expected indentation indicator in the range 1-9, but found 0",
                        self.get_mark())
            self.forward()
            ch = self.peek()
            if ch in '+-':
                if ch == '+':
                    chomping = True
                else:
                    chomping = False
                self.forward()
        ch = self.peek()
        if ch not in '\0 \r\n\x85\u2028\u2029':
            raise ScannerError("while scanning a block scalar", start_mark,
                    "expected chomping or indentation indicators, but found %r"
                    % ch, self.get_mark())
        return chomping, increment

    def scan_block_scalar_ignored_line(self, start_mark):
        # See the specification for details.
        while self.peek() == ' ':
            self.forward()
        if self.peek() == '#':
            while self.peek() not in '\0\r\n\x85\u2028\u2029':
                self.forward()
        ch = self.peek()
        if ch not in '\0\r\n\x85\u2028\u2029':
            raise ScannerError("while scanning a block scalar", start_mark,
                    "expected a comment or a line break, but found %r" % ch,
                    self.get_mark())
        self.scan_line_break()

    def scan_block_scalar_indentation(self):
        # See the specification for details.
        chunks = []
        max_indent = 0
        end_mark = self.get_mark()
        while self.peek() in ' \r\n\x85\u2028\u2029':
            if self.peek() != ' ':
                chunks.append(self.scan_line_break())
                end_mark = self.get_mark()
            else:
                self.forward()
                if self.column > max_indent:
                    max_indent = self.column
        return chunks, max_indent, end_mark

    def scan_block_scalar_breaks(self, indent):
        # See the specification for details.
        chunks = []
        end_mark = self.get_mark()
        while self.column < indent and self.peek() == ' ':
            self.forward()
        while self.peek() in '\r\n\x85\u2028\u2029':
            chunks.append(self.scan_line_break())
            end_mark = self.get_mark()
            while self.column < indent and self.peek() == ' ':
                self.forward()
        return chunks, end_mark

    def scan_flow_scalar(self, style):
        # See the specification for details.
        # Note that we loose indentation rules for quoted scalars. Quoted
        # scalars don't need to adhere indentation because " and ' clearly
        # mark the beginning and the end of them. Therefore we are less
        # restrictive then the specification requires. We only need to check
        # that document separators are not included in scalars.
        if style == '"':
            double = True
        else:
            double = False
        chunks = []
        start_mark = self.get_mark()
        quote = self.peek()
        self.forward()
        chunks.extend(self.scan_flow_scalar_non_spaces(double, start_mark))
        while self.peek() != quote:
            chunks.extend(self.scan_flow_scalar_spaces(double, start_mark))
            chunks.extend(self.scan_flow_scalar_non_spaces(double, start_mark))
        self.forward()
        end_mark = self.get_mark()
        return ('<scalar>', start_mark, end_mark, False, style, ''.join(chunks))

    ESCAPE_REPLACEMENTS = {
        '0':    '\0',
        'a':    '\x07',
        'b':    '\x08',
        't':    '\x09',
        '\t':   '\x09',
        'n':    '\x0A',
        'v':    '\x0B',
        'f':    '\x0C',
        'r':    '\x0D',
        'e':    '\x1B',
        ' ':    '\x20',
        '\"':   '\"',
        '\\':   '\\',
        '/':    '/',
        'N':    '\x85',
        '_':    '\xA0',
        'L':    '\u2028',
        'P':    '\u2029',
    }

    ESCAPE_CODES = {
        'x':    2,
        'u':    4,
        'U':    8,
    }

    def scan_flow_scalar_non_spaces(self, double, start_mark):
        # See the specification for details.
        chunks = []
        while True:
            length = 0
            while self.peek(length) not in '\'\"\\\0 \t\r\n\x85\u2028\u2029':
                length += 1
            if length:
                chunks.append(self.prefix(length))
                self.forward(length)
            ch = self.peek()
            if not double and ch == '\'' and self.peek(1) == '\'':
                chunks.append('\'')
                self.forward(2)
            elif (double and ch == '\'') or (not double and ch in '\"\\'):
                chunks.append(ch)
                self.forward()
            elif double and ch == '\\':
                self.forward()
                ch = self.peek()
                if ch in self.ESCAPE_REPLACEMENTS:
                    chunks.append(self.ESCAPE_REPLACEMENTS[ch])
                    self.forward()
                elif ch in self.ESCAPE_CODES:
                    length = self.ESCAPE_CODES[ch]
                    self.forward()
                    for k in range(length):
                        if self.peek(k) not in '0123456789ABCDEFabcdef':
                            raise ScannerError("while scanning a double-quoted scalar", start_mark,
                                    "expected escape sequence of %d hexadecimal numbers, but found %r" %
                                        (length, self.peek(k)), self.get_mark())
                    code = int(self.prefix(length), 16)
                    chunks.append(chr(code))
                    self.forward(length)
                elif ch in '\r\n\x85\u2028\u2029':
                    self.scan_line_break()
                    chunks.extend(self.scan_flow_scalar_breaks(double, start_mark))
                else:
                    raise ScannerError("while scanning a double-quoted scalar", start_mark,
                            "found unknown escape character %r" % ch, self.get_mark())
            else:
                return chunks

    def scan_flow_scalar_spaces(self, double, start_mark):
        # See the specification for details.
        chunks = []
        length = 0
        while self.peek(length) in ' \t':
            length += 1
        whitespaces = self.prefix(length)
        self.forward(length)
        ch = self.peek()
        if ch == '\0':
            raise ScannerError("while scanning a quoted scalar", start_mark,
                    "found unexpected end of stream", self.get_mark())
        elif ch in '\r\n\x85\u2028\u2029':
            line_break = self.scan_line_break()
            breaks = self.scan_flow_scalar_breaks(double, start_mark)
            if line_break != '\n':
                chunks.append(line_break)
            elif not breaks:
                chunks.append(' ')
            chunks.extend(breaks)
        else:
            chunks.append(whitespaces)
        return chunks

    def scan_flow_scalar_breaks(self, double, start_mark):
        # See the specification for details.
        chunks = []
        while True:
            # Instead of checking indentation, we check for document
            # separators.
            prefix = self.prefix(3)
            if (prefix == '---' or prefix == '...')   \
                    and self.peek(3) in '\0 \t\r\n\x85\u2028\u2029':
                raise ScannerError("while scanning a quoted scalar", start_mark,
                        "found unexpected document separator", self.get_mark())
            while self.peek() in ' \t':
                self.forward()
            if self.peek() in '\r\n\x85\u2028\u2029':
                chunks.append(self.scan_line_break())
            else:
                return chunks

    def scan_plain(self):
        # See the specification for details.
        # We add an additional restriction for the flow context:
        #   plain scalars in the flow context cannot contain ',' or '?'.
        # We also keep track of the `allow_simple_key` flag here.
        # Indentation rules are loosed for the flow context.
        chunks = []
        start_mark = self.get_mark()
        end_mark = start_mark
        indent = self.indent+1
        # We allow zero indentation for scalars, but then we need to check for
        # document separators at the beginning of the line.
        #if indent == 0:
        #    indent = 1
        spaces = []
        while True:
            length = 0
            if self.peek() == '#':
                break
            while True:
                ch = self.peek(length)
                if ch in '\0 \t\r\n\x85\u2028\u2029'    \
                        or (ch == ':' and
                                self.peek(length+1) in '\0 \t\r\n\x85\u2028\u2029'
                                      + (u',[]{}' if self.flow_level else u''))\
                        or (self.flow_level and ch in ',?[]{}'):
                    break
                length += 1
            if length == 0:
                break
            self.allow_simple_key = False
            chunks.extend(spaces)
            chunks.append(self.prefix(length))
            self.forward(length)
            end_mark = self.get_mark()
            spaces = self.scan_plain_spaces(indent, start_mark)
            if not spaces or self.peek() == '#' \
                    or (not self.flow_level and self.column < indent):
                break
        return ('<scalar>', start_mark, end_mark, True, None, ''.join(chunks))

    def scan_plain_spaces(self, indent, start_mark):
        # See the specification for details.
        # The specification is really confusing about tabs in plain scalars.
        # We just forbid them completely. Do not use tabs in YAML!
        chunks = []
        length = 0
        while self.peek(length) in ' ':
            length += 1
        whitespaces = self.prefix(length)
        self.forward(length)
        ch = self.peek()
        if ch in '\r\n\x85\u2028\u2029':
            line_break = self.scan_line_break()
            self.allow_simple_key = True
            prefix = self.prefix(3)
            if (prefix == '---' or prefix == '...')   \
                    and self.peek(3) in '\0 \t\r\n\x85\u2028\u2029':
                return
            breaks = []
            while self.peek() in ' \r\n\x85\u2028\u2029':
                if self.peek() == ' ':
                    self.forward()
                else:
                    breaks.append(self.scan_line_break())
                    prefix = self.prefix(3)
                    if (prefix == '---' or prefix == '...')   \
                            and self.peek(3) in '\0 \t\r\n\x85\u2028\u2029':
                        return
            if line_break != '\n':
                chunks.append(line_break)
            elif not breaks:
                chunks.append(' ')
            chunks.extend(breaks)
        elif whitespaces:
            chunks.append(whitespaces)
        return chunks

    def scan_tag_handle(self, name, start_mark):
        # See the specification for details.
        # For some strange reasons, the specification does not allow '_' in
        # tag handles. I have allowed it anyway.
        ch = self.peek()
        if ch != '!':
            raise ScannerError("while scanning a %s" % name, start_mark,
                    "expected '!', but found %r" % ch, self.get_mark())
        length = 1
        ch = self.peek(length)
        if ch != ' ':
            while '0' <= ch <= '9' or 'A' <= ch <= 'Z' or 'a' <= ch <= 'z'  \
                    or ch in '-_':
                length += 1
                ch = self.peek(length)
            if ch != '!':
                self.forward(length)
                raise ScannerError("while scanning a %s" % name, start_mark,
                        "expected '!', but found %r" % ch, self.get_mark())
            length += 1
        value = self.prefix(length)
        self.forward(length)
        return value

    def scan_tag_uri(self, name, start_mark):
        # See the specification for details.
        # Note: we do not check if URI is well-formed.
        chunks = []
        length = 0
        ch = self.peek(length)
        while '0' <= ch <= '9' or 'A' <= ch <= 'Z' or 'a' <= ch <= 'z'  \
                or ch in '-;/?:@&=+$,_.!~*\'()[]%':
            if ch == '%':
                chunks.append(self.prefix(length))
                self.forward(length)
                length = 0
                chunks.append(self.scan_uri_escapes(name, start_mark))
            else:
                length += 1
            ch = self.peek(length)
        if length:
            chunks.append(self.prefix(length))
            self.forward(length)
            length = 0
        if not chunks:
            raise ScannerError("while parsing a %s" % name, start_mark,
                    "expected URI, but found %r" % ch, self.get_mark())
        return ''.join(chunks)

    def scan_uri_escapes(self, name, start_mark):
        # See the specification for details.
        codes = []
        mark = self.get_mark()
        while self.peek() == '%':
            self.forward()
            for k in range(2):
                if self.peek(k) not in '0123456789ABCDEFabcdef':
                    raise ScannerError("while scanning a %s" % name, start_mark,
                            "expected URI escape sequence of 2 hexadecimal numbers, but found %r"
                            % self.peek(k), self.get_mark())
            codes.append(int(self.prefix(2), 16))
            self.forward(2)
        try:
            value = bytes(codes).decode('utf-8')
        except UnicodeDecodeError as exc:
            raise ScannerError("while scanning a %s" % name, start_mark, str(exc), mark)
        return value

    def scan_line_break(self):
        # Transforms:
        #   '\r\n'      :   '\n'
        #   '\r'        :   '\n'
        #   '\n'        :   '\n'
        #   '\x85'      :   '\n'
        #   '\u2028'    :   '\u2028'
        #   '\u2029     :   '\u2029'
        #   default     :   ''
        ch = self.peek()
        if ch in '\r\n\x85':
            if self.prefix(2) == '\r\n':
                self.forward(2)
            else:
                self.forward()
            return '\n'
        elif ch in '\u2028\u2029':
            self.forward()
            return ch
        return ''

    ########
    # Parser
    ########

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
            event = ("AliasEvent", token[1], token[2], token[3])
            self.state = self.states.pop()
        else:
            anchor = None
            tag = None
            start_mark = end_mark = tag_mark = None
            if self.check_token('<anchor>'):
                token = self.get_token()
                start_mark = token[1]
                end_mark = token[2]
                anchor = token[3]
                if self.check_token('<tag>'):
                    token = self.get_token()
                    tag_mark = token[1]
                    end_mark = token[2]
                    tag = token[3]
            elif self.check_token('<tag>'):
                token = self.get_token()
                start_mark = tag_mark = token[1]
                end_mark = token[2]
                tag = token[3]
                if self.check_token('<anchor>'):
                    token = self.get_token()
                    end_mark = token[2]
                    anchor = token[3]
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
                    event = ("ScalarEvent", start_mark, end_mark, anchor, tag, implicit, token[4], token[5])
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
                    event = ("ScalarEvent", start_mark, end_mark, anchor, tag, implicit, '', '')
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
                event = ("MappingStartEvent", token[1], token[2], "", "", False, '')
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

    ### Compose

    def compose_stream(self):
        if not self.peek_event()[0] == "StreamStartEvent":
            raise ComposerError(None, None, f"expected StreamStartEvent not {self.peek_event()[0]}")

        # Compose the root node.
        start_event = self.get_event()
        node = hif_create()
        hif_add_node(node, 0, kind="stream")
        hif_add_edge(node, 1, kind="event", tag=start_event[0])
        hif_add_incidence(node, 1, 0)

        while not self.peek_event()[0] == "StreamEndEvent":
            # TODO why do we pass a non-existing index?
            self.compose_document(node, 0, hif_number_of_all(node))

        end_event = self.get_event()
        k = hif_number_of_all(node)
        hif_add_edge(node, k, kind="event", tag=end_event[0])
        hif_add_incidence(node, k, 0)

        self.anchors = {}
        return node

    def compose_document(self, node, parent, index):
        if not self.peek_event()[0] == "DocumentStartEvent":
            raise ComposerError(None, None, f"expected DocumentStartEvent not {self.peek_event()[0]}")

        # Drop the DOCUMENT-START event.
        start_event = self.get_event()

        # Compose the root node.
        hif_add_node(node, index, kind="document")
        hif_add_edge(node, index+1, kind="event", tag=start_event[0])
        hif_add_incidence(node, index+1, index, "tail")
        hif_add_incidence(node, index+1, parent)
        # TODO why do we pass a non-existing index?
        self.compose_node(node, index, index+2)

        if not self.peek_event()[0] == "DocumentEndEvent":
            raise ComposerError(None, None, f"expected DocumentEndEvent not {self.peek_event()[0]}")

        # Drop the DOCUMENT-END event.
        end_event = self.get_event()
        k = hif_number_of_all(node)
        hif_add_edge(node, k, kind="event", tag=end_event[0])
        hif_add_incidence(node, k, index, "tail")

        self.anchors = {}

    def compose_node(self, node, parent, index):
        if self.peek_event()[0] == "AliasEvent":
            self.compose_alias_node(node, parent, index)
        elif self.peek_event()[0] == "ScalarEvent":
            self.compose_scalar_node(node, parent, index)
        elif self.peek_event()[0] == "SequenceStartEvent":
            self.compose_sequence_node(node, parent, index)
        elif self.peek_event()[0] == "MappingStartEvent":
            self.compose_mapping_node(node, parent, index)
        else:
            raise ComposerError(None, None, f"unexpected event {self.peek_event()[0]}")

    def compose_alias_node(self, node, parent, index):
        if not self.peek_event()[0] == "AliasEvent":
            raise ComposerError(None, None, f"unexpected event {self.peek_event()[0]}")
        event = self.get_event()
        (start_event_name, start_mark, end_mark, anchor) = event
        (start_mark_name, start_mark_index, start_mark_line, start_mark_column, start_mark_buffer, start_mark_pointer) = (start_mark.name, start_mark.index, start_mark.line, start_mark.column, start_mark.buffer, start_mark.pointer)
        (end_mark_name, end_mark_index, end_mark_line, end_mark_column, end_mark_buffer, end_mark_pointer) = (end_mark.name, end_mark.index, end_mark.line, end_mark.column, end_mark.buffer, end_mark.pointer)
        hif_add_node(node, index,
                start_mark_name=start_mark_name or "", start_mark_index=start_mark_index or "", start_mark_line=start_mark_line or "", start_mark_column=start_mark_column or "", start_mark_buffer=start_mark_buffer or "", start_mark_pointer=start_mark_pointer or "",
                end_mark_name=end_mark_name or "", end_mark_index=end_mark_index or "", end_mark_line=end_mark_line or "", end_mark_column=end_mark_column or "", end_mark_buffer=end_mark_buffer or "", end_mark_pointer=end_mark_pointer or "",
                kind="alias", anchor=anchor or "")
        hif_add_edge(node, index+1, kind="event", tag=start_event_name)
        hif_add_incidence(node, index+1, index, "tail")
        hif_add_incidence(node, parent+1, index, "tail")
        hif_add_incidence(node, index+1, parent, event=event)
        return node

    def compose_scalar_node(self, node, parent, index):
        if not self.peek_event()[0] == "ScalarEvent":
            raise ComposerError(None, None, f"unexpected event {self.peek_event()[0]}")
        event = self.get_event()
        (start_event_name, start_mark, end_mark, anchor, tag, implicit, style, value) = event
        (start_mark_name, start_mark_index, start_mark_line, start_mark_column, start_mark_buffer, start_mark_pointer) = (start_mark.name, start_mark.index, start_mark.line, start_mark.column, start_mark.buffer, start_mark.pointer)
        (end_mark_name, end_mark_index, end_mark_line, end_mark_column, end_mark_buffer, end_mark_pointer) = (end_mark.name, end_mark.index, end_mark.line, end_mark.column, end_mark.buffer, end_mark.pointer)
        hif_add_node(node, index,
                implicit=implicit or "",
                start_mark_name=start_mark_name or "", start_mark_index=start_mark_index or "", start_mark_line=start_mark_line or "", start_mark_column=start_mark_column or "", start_mark_buffer=start_mark_buffer or "", start_mark_pointer=start_mark_pointer or "",
                end_mark_name=end_mark_name or "", end_mark_index=end_mark_index or "", end_mark_line=end_mark_line or "", end_mark_column=end_mark_column or "", end_mark_buffer=end_mark_buffer or "", end_mark_pointer=end_mark_pointer or "",
                style=style or "",
                kind="scalar", tag=tag or "", value=value or "", anchor=anchor or "")
        hif_add_edge(node, index+1, kind="event", tag=start_event_name)
        hif_add_incidence(node, index+1, index, "tail")
        hif_add_incidence(node, index+1, parent)
        return node

    def compose_sequence_node(self, node, parent, index):
        if not self.peek_event()[0] == "SequenceStartEvent":
            raise ComposerError(None, None, f"unexpected event {self.peek_event()[0]}")
        start_event = self.get_event()
        (start_event_name, start_mark, end_mark, anchor, tag, implicit, flow_style) = start_event
        (start_mark_name, start_mark_index, start_mark_line, start_mark_column, start_mark_buffer, start_mark_pointer) = (start_mark.name, start_mark.index, start_mark.line, start_mark.column, start_mark.buffer, start_mark.pointer)
        (end_mark_name, end_mark_index, end_mark_line, end_mark_column, end_mark_buffer, end_mark_pointer) = (end_mark.name, end_mark.index, end_mark.line, end_mark.column, end_mark.buffer, end_mark.pointer)
        hif_add_node(node, index,
                implicit=implicit or "",
                start_mark_name=start_mark_name or "", start_mark_index=start_mark_index or "", start_mark_line=start_mark_line or "", start_mark_column=start_mark_column or "", start_mark_buffer=start_mark_buffer or "", start_mark_pointer=start_mark_pointer or "",
                end_mark_name=end_mark_name or "", end_mark_index=end_mark_index or "", end_mark_line=end_mark_line or "", end_mark_column=end_mark_column or "", end_mark_buffer=end_mark_buffer or "", end_mark_pointer=end_mark_pointer or "",
                flow_style=flow_style or "",
                kind="sequence", tag=tag or "", anchor=anchor or "")
        hif_add_edge(node, index+1, kind="event", tag=start_event_name)
        hif_add_incidence(node, index+1, index, "tail")
        hif_add_incidence(node, parent+1, index, "tail")
        hif_add_incidence(node, index+1, parent, start_event=start_event)
        while not self.peek_event()[0] == "SequenceEndEvent":
            k = hif_number_of_all(node)
            self.compose_node(node, index, k)
        end_event = self.get_event()
        k = hif_number_of_all(node)
        hif_add_edge(node, k, kind="event", tag=end_event[0])
        hif_add_incidence(node, k, parent, end_event=end_event)
        return node

    def compose_mapping_node(self, node, parent, index):
        if not self.peek_event()[0] == "MappingStartEvent":
            raise ComposerError(None, None, f"unexpected event {self.peek_event()[0]}")
        start_event = self.get_event()
        (start_event_name, start_mark, end_mark, anchor, tag, implicit, flow_style) = start_event
        (start_mark_name, start_mark_index, start_mark_line, start_mark_column, start_mark_buffer, start_mark_pointer) = (start_mark.name, start_mark.index, start_mark.line, start_mark.column, start_mark.buffer, start_mark.pointer)
        (end_mark_name, end_mark_index, end_mark_line, end_mark_column, end_mark_buffer, end_mark_pointer) = (end_mark.name, end_mark.index, end_mark.line, end_mark.column, end_mark.buffer, end_mark.pointer)
        hif_add_node(node, index,
                implicit=implicit or "",
                start_mark_name=start_mark_name or "", start_mark_index=start_mark_index or "", start_mark_line=start_mark_line or "", start_mark_column=start_mark_column or "", start_mark_buffer=start_mark_buffer or "", start_mark_pointer=start_mark_pointer or "",
                end_mark_name=end_mark_name or "", end_mark_index=end_mark_index or "", end_mark_line=end_mark_line or "", end_mark_column=end_mark_column or "", end_mark_buffer=end_mark_buffer or "", end_mark_pointer=end_mark_pointer or "",
                flow_style=flow_style or "",
                kind="mapping", tag=tag or "", anchor=anchor or "")
        hif_add_edge(node, index+1, kind="event", tag=start_event_name)
        hif_add_incidence(node, index+1, index, "tail")
        hif_add_incidence(node, index+1, parent)

        while not self.peek_event()[0] == "MappingEndEvent":
            k = hif_number_of_all(node)
            self.compose_node(node, index, k)
            v = hif_number_of_all(node)
            self.compose_node(node, index, v)

        end_event = self.get_event()
        k = hif_number_of_all(node)
        hif_add_edge(node, k, kind="event", tag=end_event[0])
        hif_add_incidence(node, k, parent)
        return node
