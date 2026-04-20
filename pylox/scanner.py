from pylox.token import TokenType, Token
from pylox.error_reporter import error


class Scanner:
    KEYWORDS = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
    }


    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def _is_at_end(self):
        return self.current >= len(self.source)

    def _advance(self):
        char = self.source[self.current]
        self.current += 1
        return char

    def _add_token(self, token_type: TokenType, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def _match(self, expected: str) -> bool:
        if self._is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def _peek(self) -> str:
        if self._is_at_end():
            return '\0'
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def _string(self) -> None:
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == '\n':
                self.line += 1
            self._advance()
        
        if self._is_at_end():
            error(self.line, "Unterminated String")
            return

        self._advance()

        str_value = self.source[self.start + 1:self.current - 1]
        self._add_token(TokenType.STRING, str_value)

    def _number(self) -> None:
        while self._peek().isdigit():
            self._advance()
        
        if self._peek() == "." and self._peek_next().isdigit():
            self._advance()
            while self._peek().isdigit():
                self._advance()

        val = float(self.source[self.start:self.current])     
        self._add_token(TokenType.NUMBER, val)

    def _identifier(self):
        while self._peek().isalnum() or self._peek() == '_':
            self._advance()
        
        text = self.source[self.start:self.current]
        token_type = Scanner.KEYWORDS.get(text, TokenType.IDENTIFIER)
        self._add_token(token_type)




    def _scan_token(self):
        c = self._advance()

        match c:
            case '(':
                self._add_token(TokenType.LEFT_PAREN)
            case ')':
                self._add_token(TokenType.RIGHT_PAREN)
            case '{':
                self._add_token(TokenType.LEFT_BRACE)
            case '}':
                self._add_token(TokenType.RIGHT_BRACE)

            case ',':
                self._add_token(TokenType.COMMA)
            case '.':
                self._add_token(TokenType.DOT)
            case '-':
                self._add_token(TokenType.MINUS)
            case '+':
                self._add_token(TokenType.PLUS)
            case ';':
                self._add_token(TokenType.SEMICOLON)
            case '*':
                self._add_token(TokenType.STAR)
            # One or two character tokens
            case '!':
                self._add_token(TokenType.BANG_EQUAL if self._match('=') else TokenType.BANG)
            case '=':
                self._add_token(TokenType.EQUAL_EQUAL if self._match('=') else TokenType.EQUAL)
            case '<':
                self._add_token(TokenType.LESS_EQUAL if self._match('=') else TokenType.LESS)
            case '>':
                self._add_token(TokenType.GREATER_EQUAL if self._match('=') else TokenType.GREATER)
            # Comments or slash
            case '/':
                if self._match('/'):
                    while self._peek() != '\n' and not self._is_at_end():
                        self._advance()
                elif self._match('*'):
                    while not self._is_at_end():
                        if self._peek() == '\n':
                            self.line += 1
                        if self._peek() == '*' and self._peek_next() == '/':
                            self._advance()
                            self._advance()
                            break
                        self._advance()
                    else:
                        error(self.line, "Unterminated block comment.")
                else:
                    self._add_token(TokenType.SLASH)
            # Whitespace
            case ' ' | '\r' | '\t':
                pass
            case '\n':
                self.line += 1
            # String literals
            case '"':
                self._string()
            case c if c.isdigit():
                self._number()
            case c if c.isalpha() or c == "_":
                self._identifier()
            case _:
                error(self.line, "Unexpected character.")
