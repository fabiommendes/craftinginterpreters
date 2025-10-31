import pytest
from lox.testing import check_program


@pytest.mark.parametrize("name", ["empty"])
def test_block(name: str):
    check_program("block", name)


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
def test_for(name: str):
    check_program("for", name)


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
def test_if(name: str):
    check_program("if", name)


@pytest.mark.parametrize(
    "name",
    [
        "and",
        "and_truth",
        "or",
        "or_truth",
    ],
)
def test_logical_operator(name: str):
    check_program("logical_operator", name)


@pytest.mark.parametrize("name", ["syntax", "var_in_body"])
def test_while(name: str):
    check_program("while", name)
