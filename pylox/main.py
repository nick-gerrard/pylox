import sys
from pathlib import Path
import pylox.error_reporter as error_reporter
from pylox.scanner import Scanner
from pylox.parser import Parser
from pylox.interpreter import Interpreter

interpreter = Interpreter()

def main():
    args = sys.argv[1:]
    if len(args) > 1:
        print("Usage: pylox [script]")
        sys.exit(64)
    elif len(args) == 1:
        run_file(args[0])
    else:
        run_prompt()


def run_file(path: str):
    source = Path(path).read_text()
    run(source)
    if error_reporter.had_error:
        sys.exit(65)


def run_prompt():
    while True:
        try:
            line = input("> ")
        except EOFError:
            break
            
        run(line)
        error_reporter.had_error = False


def run(source):
    global interpreter

    scanner = Scanner(source=source)
    tokens = scanner.scan_tokens()

    parser = Parser(tokens)
    statements = parser.parse()
    if statements is None:
        return

    if error_reporter.had_error:
        return

    interpreter.interpret(statements)

if __name__ == "__main__":
    main()