import pytest


@pytest.mark.parametrize("name", ["to_this"])
def test_assignment(check, name: str):
    check("assignment", name)


@pytest.mark.parametrize("name", ["object"])
def test_call(check, name: str):
    check("call", name)


@pytest.mark.parametrize(
    "name",
    ["empty", "local_reference_self", "reference_self"],
)
def test_class(check, name: str):
    check("class", name)


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
def test_constructor(check, name: str):
    check("constructor", name)


@pytest.mark.parametrize("name", ["class_in_else", "class_in_then"])
def test_if(check, name: str):
    check("if", name)


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
def test_field(check, name: str):
    check("field", name)


@pytest.mark.parametrize("name", ["class_in_body"])
def test_for(check, name: str):
    check("for", name)


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
def test_method(check, name: str):
    check("method", name)


@pytest.mark.parametrize("name", ["in_method"])
def test_return(check, name: str):
    check("return", name)


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
def test_this(check, name: str):
    check("this", name)


@pytest.mark.parametrize("name", ["class_in_body"])
def test_while(check, name: str):
    check("while", name)


@pytest.mark.parametrize("name", ["local_from_method"])
def test_variable(check, name: str):
    check("variable", name)
