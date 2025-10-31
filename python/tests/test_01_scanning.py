"""
This test module assumes that lox:tokenize or lox.scanner:tokenize is available
and has the signature `tokenize(str) -> list[Token]`.

The tokens should have a __str__ method that produces a representation like:

    <TokenType> <lexeme> <literal>

It may contain additional information, but that will be ignored by the tests.
"""

from dataclasses import dataclass
from functools import cached_property
from itertools import count
from pathlib import Path
from typing import Iterator

TEST_BASE = Path(__file__).parent.parent / "examples" / "scanning"


#
# Parse examples
#


class Result:
    line: int
    message: str


@dataclass
class Example:
    source: str
    expect: list[Result]

    def had_errors(self) -> bool:
        return not all(isinstance(r, Expect) for r in self.expect)

    def had_syntax_errors(self) -> bool:
        return any(isinstance(r, (Error, ErrorAt, ErrorAtEnd)) for r in self.expect)

    def output_lines(self) -> list[str]:
        return [r.message for r in self.expect if isinstance(r, Expect)]

    def stdout(self) -> str:
        return "\n".join(self.output_lines())


@dataclass
class Expect(Result):
    line: int
    message: str


@dataclass
class ExpectRuntimeError(Result):
    line: int
    message: str


@dataclass
class Error(Result):
    line: int
    message: str


@dataclass
class ErrorAt(Error):
    token: str


@dataclass
class ErrorAtEnd(Error):
    pass


def example(soure_or_path: str | Path) -> "Example":
    """
    Return an example from a file or source string.
    """
    if isinstance(soure_or_path, Path):
        if not soure_or_path.exists():
            raise FileNotFoundError(f"no such file: {soure_or_path}")
        source = soure_or_path.read_text()
    else:
        source = soure_or_path
    return parse_example(source)


def parse_example(source: str) -> "Example":
    """
    Parse a source string into an Example object.
    """
    expect: list[Result] = []
    for line_no, line in enumerate(source.splitlines(), start=1):
        line = line.strip()
        _, sep, comment = line.partition("//")
        if not sep:
            continue
        comment = comment.strip()

        if comment.startswith(prefix := "expect:"):
            message = comment.removeprefix(prefix).strip()
            expect.append(Expect(line=line_no, message=message))
        elif comment.startswith(prefix := "Error at end:"):
            message = comment.removeprefix(prefix).strip()
            expect.append(ErrorAtEnd(line=line_no, message=message))
        elif comment.startswith(prefix := "Error at '"):
            rest = comment.removeprefix(prefix)
            token, sep, message = rest.partition("':")
            if not sep:
                raise ValueError(f"malformed error at: {comment!r}")
            message = message.strip()
            expect.append(ErrorAt(line=line_no, message=message, token=token))
        elif comment.startswith(prefix := "Error:"):
            message = comment.removeprefix(prefix).strip()
            expect.append(Error(line=line_no, message=message))
        elif comment.startswith(prefix := "expect runtime error:"):
            message = comment.removeprefix(prefix).strip()
            expect.append(ExpectRuntimeError(line=line_no, message=message))

    return Example(source, expect=expect)


def mod(name: str):
    if ":" in name:
        module_name, _, attr = name.partition(":")
        mod = _mod(module_name)
        try:
            return getattr(mod, attr)
        except AttributeError as e:
            msg = f"module lox.{module_name!r} has no attribute {attr!r}, did you forget to define it?"
            raise RuntimeError(msg) from e
    else:
        return _mod(name)


def _mod(name: str):
    import importlib

    try:
        module = importlib.import_module("lox." + name)
    except ImportError as e:
        msg = f"could not import lox.{name!r}, are you sure you created a `lox/{name}.py` file?"
        raise RuntimeError(msg) from e
    return module


class ScannerBase:
    file: str

    @cached_property
    def example(self) -> Example:
        path = TEST_BASE / f"{self.file}.lox"
        return example(path)

    def expected_tokens(self) -> Iterator[str]:
        for line in self.example.output_lines():
            yield normalize_token_representation(line)

    def scan_tokens(self) -> Iterator[str]:
        tokenize = mod("scanner:tokenize")

        for token in tokenize(self.example.source):
            yield normalize_token_representation(str(token))

    def test_scanner(self):
        parsed = self.scan_tokens()
        answers = self.expected_tokens()
        for i, got, expected in zip(count(1), parsed, answers):
            if got == expected or got.startswith(expected):
                continue
            assert got == expected, f"line {i}: got {got!r}, expected {expected!r}"


class TestIdentifiers(ScannerBase):
    file = "identifiers"


class TestKeywords(ScannerBase):
    file = "keywords"


class TestNumbers(ScannerBase):
    file = "numbers"


class TestPunctuation(ScannerBase):
    file = "punctuators"


class TestStrings(ScannerBase):
    file = "strings"


class TestWhitesoace(ScannerBase):
    file = "whitespace"


def normalize_token_representation(line: str) -> str:
    if line.endswith("null"):
        line = line[:-4] + "None"
    line = line.replace("'", "").rstrip()
    return line
