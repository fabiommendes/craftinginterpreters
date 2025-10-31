import io
import pathlib
from contextlib import redirect_stdout

import pytest

EXAMPLES = {"root": ["empty_file", "precedence", "unexpected_character"]}
BASE = pathlib.Path(__file__).parent.parent.parent / "test"
SKIP_MODULES = ["scanning", "benchmark", "expressions"]
SKIP_EXAMPLES = {}

for mod_path in BASE.iterdir():
    if mod_path.is_dir() and mod_path.name not in SKIP_MODULES:
        mod = mod_path.name
        for file_path in mod_path.iterdir():
            if file_path.suffix == ".lox" and file_path.stem not in SKIP_EXAMPLES.get(
                mod, []
            ):
                name = file_path.stem
                EXAMPLES.setdefault(mod, []).append(name)


@pytest.mark.parametrize("mod, examples", EXAMPLES.items(), ids=EXAMPLES.keys())
def test_example(check, mod: str, examples: list[str]):
    print(f"Testing module: {mod}")
    if mod == "root":
        mod = ""
    for name in examples:
        error = None
        with redirect_stdout(io.StringIO()) as f:
            try:
                check(mod, name)
                print(f"Test {name} passed.")
                continue
            except Exception as e:
                error = e.with_traceback(e.__traceback__)

        print(f"Error occurred while testing {name}: {error}")
        print(f.getvalue())
        raise error
