import sys
from pylox.token import TokenType, Token

had_error = False
had_runtime_error = False

def error(line: int, message: str):
    report(line, "", message)

def token_error(token: Token, message: str):
    if token.token_type == TokenType.EOF:
        report(token.line, "at end", message)
    else:
        report(token.line, f"at '{token.lexeme}'", message)

def runtime_error(error):
    global had_runtime_error
    print(f"Error{error.message}\n[line {error.token.line}]", file=sys.stderr)
    had_runtime_error = True

def report(line: int, where: str, message: str):
    global had_error
    print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
    had_error = True
