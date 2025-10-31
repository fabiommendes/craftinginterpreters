import re
from contextlib import redirect_stdout
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

from lox.__main__ import Lox

LINE_PATTERN = re.compile(r"^\[line (\d+)\] ")


def parse_expects(src: str) -> str:
    """
    Return the expected output lines from a source string.
    """
    lines = []
    for line in src.splitlines():
        line = line.strip()
        _, sep, comment = line.partition("//")
        if not sep:
            continue
        comment = comment.lstrip()

        if comment.startswith(prefix := "expect:"):
            message = comment.removeprefix(prefix).strip()
            lines.append(message)
        elif comment.startswith(prefix := "expect "):
            message = comment.removeprefix(prefix).strip()
            lines.append(message)
        elif comment.startswith("Error at"):
            lines.append(comment)
        elif comment.startswith("[c"):
            continue
        elif comment.startswith(prefix := "[java"):
            lines.append("[" + comment.removeprefix("[java").lstrip())
        elif comment.startswith("["):
            lines.append(comment)

    return "\n".join(lines)


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


#
# Parse examples
#
class Result:
    line: int
    message: str


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


#
# Test programs
#
def check_program(section: str, name: str, /):
    """
    Check if a program produces the expected output.

    Usually used in this pattern:

        @pytest.mark.parametrize("name", ["prog1", "prog2", ...])
        def test_some_feature(name: str):
            check_program("some_section", name)
    """
    base = Path(__file__).parent.parent.parent / "test"
    if section:
        path = base / section / f"{name}.lox"
    else:
        path = base / f"{name}.lox"
    source = path.read_text()

    print(f"Testing program: {path.relative_to(base)}\n")
    print(ident(source, "  "))
    print()

    expected = parse_expects(source)
    print("Expected output:\n")
    print(ident(expected, "  "))
    print()

    lox = Lox(interactive=True)
    err = None
    with redirect_stdout(StringIO()) as f:
        try:
            lox.run(source)
        except Exception as e:
            err = e
            print(f"Runtime error: {err}")
            err.with_traceback(err.__traceback__)

    output = f.getvalue().rstrip()
    print("Actual output:\n")
    print(ident(output, "  "))
    print()

    if err is not None:
        raise err
    else:
        compare_output(output, expected)


def compare_output(stdout: str, expected_stdout: str):
    output = stdout.rstrip().splitlines()
    expected = expected_stdout.rstrip().splitlines()
    if output == expected:
        return

    while output and expected:
        if compatible(output[0], expected[0]):
            output.pop(0)
            expected.pop(0)
            continue
        elif compatible(output[-1], expected[-1]):
            output.pop()
            expected.pop()
            continue
        raise AssertionError(
            f"expected output line: {expected[0]!r}, got: {output[0]!r}"
        )


def compatible(actual: str, expected: str) -> bool:
    if actual == expected:
        return True
    elif expected.startswith("runtime error:"):
        prefix, sep, rest = actual.partition(":")
        if sep and "Runtime error" in prefix:
            expected = expected.removeprefix("runtime error:")
            actual = rest
    elif actual.startswith("[line ") and not expected.startswith("[line "):
        _, _, actual = actual.partition("] ")
    elif (m1 := LINE_PATTERN.match(actual)) and (m2 := LINE_PATTERN.match(expected)):
        if m1.group(0) == m2.group(0):
            actual = actual[m1.end() :]
            expected = expected[m2.end() :]
            return compatible(actual, expected)
    elif actual.startswith("Error at '") and expected.startswith("Error:"):
        actual = "Error:" + actual.partition("':")[2]
    return actual == expected


def is_error_line(text: str) -> bool:
    text = text.lstrip().casefold()
    return (
        text.startswith("[line ")
        or text.startswith("error")
        or text.startswith("runtime error")
    )


def ident(s: str, prefix: str) -> str:
    return "\n".join(prefix + line for line in s.splitlines())
