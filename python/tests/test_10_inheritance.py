import pytest
from lox.testing import check_program


@pytest.mark.parametrize(
    "name",
    [
        "inherited_method",
        "local_inherit_other",
        "local_inherit_self",
        "inherit_self",
    ],
)
def test_class(name: str):
    check_program("class", name)


@pytest.mark.parametrize(
    "name",
    [
        "constructor",
        "inherit_from_function",
        "inherit_from_nil",
        "inherit_from_number",
        "inherit_methods",
        "parenthesized_superclass",
        "set_fields_from_base_class",
    ],
)
def test_inheritance(name: str):
    check_program("inheritance", name)


@pytest.mark.parametrize(
    "name",
    [
        "bound_method",
        "call_other_method",
        "call_same_method",
        "closure",
        "constructor",
        "extra_arguments",
        "indirectly_inherited",
        "missing_arguments",
        "no_superclass_bind",
        "no_superclass_call",
        "no_superclass_method",
        "parenthesized",
        "reassign_superclass",
        "super_at_top_level",
        "super_in_closure_in_inherited_method",
        "super_in_inherited_method",
        "super_in_top_level_function",
        "super_without_dot",
        "super_without_name",
        "this_in_superclass_method",
    ],
)
def test_super(name: str):
    check_program("super", name)
