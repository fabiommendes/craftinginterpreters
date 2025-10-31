# lox/lox.py
import sys
from pathlib import Path
from rich import print

from lox.scanner import tokenize
from lox.parser import parse
from lox.interpreter import exec, Env
from lox.errors import LoxRuntimeError, LoxStaticError, LoxSyntaxError
from lox.ast import *
from lox.resolver import resolve


class Lox:
    def __init__(self, interactive: bool = False):
        self.interactive = interactive
        self.environment = Env.globals()

    def run(self, source: str):
        try:
            tokens = tokenize(source)
            ast = parse(tokens)
            ast = resolve(ast)
            exec(ast, self.environment)
        except LoxRuntimeError as error:
            self.report_error(error, code=70)
        except (LoxSyntaxError, LoxStaticError) as error:
            self.report_error(error, code=65)

    def report_error(self, error: Exception, code: int):
        print(error)
        if code and not self.interactive:
            sys.exit(code)

  
def main():
    if ast := ("--ast" in sys.argv):
        sys.argv.remove("--ast")
    if show := ("--show" in sys.argv):
        sys.argv.remove("--show")
        
    if len(sys.argv) > 2:
        print("Usage: pylox [script]")
        exit(64)
    elif len(sys.argv) == 2:
        path = Path(sys.argv[1])
        if show:
            print(path.read_text())
        if ast:
            print(resolve(parse(tokenize(path.read_text()))))
        run_file(path)
    else:
        run_prompt()


def run_file(path: Path):
    src = path.read_text(encoding=sys.getdefaultencoding())
    lox = Lox()
    lox.run(src)


def run_prompt():
    lox = Lox()

    while True:
        try:
            line = input("> ")
        except EOFError:
            break
        else:
            lox.run(line)


if __name__ == "__main__":
    main()
