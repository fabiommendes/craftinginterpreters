import pytest


@pytest.mark.parametrize("name", ["bool", "nil", "string", "num"])
def test_call(check, name: str):
    check("call", name)


@pytest.mark.parametrize("name", ["syntax"])
def test_for(check, name: str):
    check("for", name)


@pytest.mark.parametrize(
    "name",
    [
        "body_must_be_block",
        "empty_body",
        "extra_arguments",
        "mutual_recursion",
        "local_recursion",
        "missing_arguments",
        "missing_comma_in_parameters",
        "nested_call_with_arguments",
        "parameters",
        "print",
        "recursion",
        "too_many_arguments",
        "too_many_parameters",
    ],
)
def test_function(check, name: str):
    check("function", name)


@pytest.mark.parametrize("name", ["fun_in_else", "fun_in_then"])
def test_if(check, name: str):
    check("if", name)


@pytest.mark.parametrize(
    "name",
    [
        "after_else",
        "after_if",
        "after_while",
        "at_top_level",
        "in_function",
        "return_nil_if_no_value",
    ],
)
def test_return(check, name: str):
    check("return", name)


@pytest.mark.parametrize(
    "name",
    ["fun_in_body", "closure_in_body", "return_closure", "return_inside"],
)
def test_while(check, name: str):
    check("while", name)
