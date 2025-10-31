import pytest
from lox.testing import check_program


@pytest.mark.parametrize("name", ["to_this"])
def test_assignment(name: str):
    check_program("assignment", name)


@pytest.mark.parametrize("name", ["object"])
def test_call(name: str):
    check_program("call", name)


@pytest.mark.parametrize(
    "name",
    ["empty", "local_reference_self", "reference_self"],
)
def test_class(name: str):
    check_program("class", name)


@pytest.mark.parametrize(
    "name",
    [
        "arguments",
        "call_init_early_return",
        "call_init_explicitly",
        "default",
        "default_arguments",
        "early_return",
        "extra_arguments",
        "init_not_method",
        "missing_arguments",
        "return_in_nested_function",
        "return_value",
    ],
)
def test_constructor(name: str):
    check_program("constructor", name)


@pytest.mark.parametrize("name", ["class_in_else", "class_in_then"])
def test_if(name: str):
    check_program("if", name)


@pytest.mark.parametrize(
    "name",
    [
        "call_function_field",
        "call_nonfunction_field",
        "get_and_set_method",
        "get_on_bool",
        "get_on_class",
        "get_on_function",
        "get_on_nil",
        "get_on_num",
        "get_on_string",
        "many",
        "method",
        "method_binds_this",
        "on_instance",
        "set_evaluation_order",
        "set_on_bool",
        "set_on_class",
        "set_on_function",
        "set_on_nil",
        "set_on_num",
        "set_on_string",
        "undefined",
    ],
)
def test_field(name: str):
    check_program("field", name)


@pytest.mark.parametrize("name", ["class_in_body"])
def test_for(name: str):
    check_program("for", name)


@pytest.mark.parametrize(
    "name",
    [
        "arity",
        "empty_block",
        "extra_arguments",
        "missing_arguments",
        "not_found",
        "print_bound_method",
        "refer_to_name",
        "too_many_arguments",
        "too_many_parameters",
    ],
)
def test_method(name: str):
    check_program("method", name)


@pytest.mark.parametrize("name", ["in_method"])
def test_return(name: str):
    check_program("return", name)


@pytest.mark.parametrize(
    "name",
    [
        "closure",
        "nested_class",
        "nested_closure",
        "this_at_top_level",
        "this_in_method",
        "this_in_top_level_function",
    ],
)
def test_this(name: str):
    check_program("this", name)


@pytest.mark.parametrize("name", ["class_in_body"])
def test_while(name: str):
    check_program("while", name)


@pytest.mark.parametrize("name", ["local_from_method"])
def test_variable(name: str):
    check_program("variable", name)
