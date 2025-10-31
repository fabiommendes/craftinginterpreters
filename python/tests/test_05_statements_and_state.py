import pytest


@pytest.mark.parametrize(
    "name",
    [
        "syntax",
        "global",
        "local",
        "undefined",
        "grouping",
        "associativity",
        "infix_operator",
        "prefix_operator",
    ],
)
def test_assignment(check, name: str):
    check("assignment", name)


@pytest.mark.parametrize("name", ["scope"])
def test_block(check, name: str):
    check("block", name)


@pytest.mark.parametrize("name", ["equality", "not"])
def test_bool(check, name: str):
    check("bool", name)


@pytest.mark.parametrize("name", ["literal"])
def test_nil(check, name: str):
    check("nil", name)


@pytest.mark.parametrize(
    "name",
    [
        "add",
        "add_bool_nil",
        "add_bool_num",
        "add_bool_string",
        "add_nil_nil",
        "add_num_nil",
        "add_string_nil",
        "comparison",
        "divide",
        "divide_nonnum_num",
        "divide_num_nonnum",
        "equals",
        "equals_class",
        "equals_method",
        "greater_nonnum_num",
        "greater_num_nonnum",
        "greater_or_equal_nonnum_num",
        "greater_or_equal_num_nonnum",
        "less_nonnum_num",
        "less_num_nonnum",
        "less_or_equal_nonnum_num",
        "less_or_equal_num_nonnum",
        "multiply",
        "multiply_nonnum_num",
        "multiply_num_nonnum",
        "negate",
        "negate_nonnum",
        "not",
        "not_class",
        "not_equals",
        "subtract",
        "subtract_nonnum_num",
        "subtract_num_nonnum",
    ],
)
def test_operator(check, name: str):
    check("operator", name)


@pytest.mark.parametrize("name", ["hello", "missing_argument"])
def test_print(check, name: str):
    check("print", name)


@pytest.mark.parametrize(
    "name", ["error_after_multiline", "literals", "multiline", "unterminated"]
)
def test_string(check, name: str):
    check("string", name)


@pytest.mark.parametrize(
    "name",
    [
        "duplicate_local",
        "duplicate_parameter",
        "in_middle_of_block",
        "in_nested_block",
        "redeclare_global",
        "redefine_global",
        "scope_reuse_in_different_blocks",
        "shadow_and_local",
        "shadow_global",
        "shadow_local",
        "undefined_global",
        "undefined_local",
        "uninitialized",
        "unreached_undefined",
        "use_global_in_initializer",
        "use_false_as_var",
        "use_nil_as_var",
        "use_this_as_var",
    ],
)
def test_variable(check, name: str):
    check("variable", name)
