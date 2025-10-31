import re
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest
from lox.__main__ import Lox

LINE_PATTERN = re.compile(r"^\[line (\d+)\] ")


@pytest.fixture
def check():
    return check_program


def check_program(section: str, name: str, /):
    """
    Check if a program produces the expected output.

    Usually used in this pattern:

        @pytest.mark.parametrize("name", ["prog1", "prog2", ...])
        def test_some_feature(check, name: str):
            check("some_section", name)
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
