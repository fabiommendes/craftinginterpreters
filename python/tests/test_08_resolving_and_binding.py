import pytest
from lox.testing import check_program


@pytest.mark.parametrize("name", ["local_mutual_recursion"])
def test_function(name: str):
    check_program("function", name)


@pytest.mark.parametrize(
    "name",
    [
        "assign_to_closure",
        "assign_to_shadowed_later",
        "close_over_function_parameter",
        "close_over_later_variable",
        "close_over_method_parameter",
        "closed_closure_in_function",
        "nested_closure",
        "open_closure_in_function",
        "reference_closure_multiple_times",
        "reuse_closure_slot",
        "shadow_closure_with_local",
        "unused_closure",
        "unused_later_closure",
    ],
)
def test_closure(name: str):
    check_program("closure", name)


@pytest.mark.parametrize(
    "name", ["early_bound", "use_local_in_initializer", "collide_with_parameter"]
)
def test_variable(name: str):
    check_program("variable", name)
