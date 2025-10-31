import pytest


@pytest.mark.parametrize("name", ["empty"])
def test_block(check, name: str):
    check("block", name)


@pytest.mark.parametrize(
    "name",
    [
        "scope",
        "var_in_body",
        "statement_condition",
        "statement_increment",
        "statement_initializer",
    ],
)
def test_for(check, name: str):
    check("for", name)


@pytest.mark.parametrize(
    "name",
    [
        "if",
        "else",
        "truth",
        "dangling_else",
        "var_in_else",
        "var_in_then",
    ],
)
def test_if(check, name: str):
    check("if", name)


@pytest.mark.parametrize(
    "name",
    [
        "and",
        "and_truth",
        "or",
        "or_truth",
    ],
)
def test_logical_operator(check, name: str):
    check("logical_operator", name)


@pytest.mark.parametrize("name", ["syntax", "var_in_body"])
def test_while(check, name: str):
    check("while", name)
