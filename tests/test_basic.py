from __future__ import annotations

import ast

import pytest
import tokenize_rt

from absolute_to_relative_sibling import replace_tokens_2


@pytest.mark.parametrize(
    "input_code,import_stmt,expected_code,expected_is_fixed",
    [
        ("from i.j import a, b, c", ["i"], "from .j import a, b, c", True),
        (
            "from i.j import a, b as new_b, c as new_c",
            ["i"],
            "from .j import a, b as new_b, c as new_c",
            True,
        ),
        ("from a.b.a import i", ["a", "b"], "from .a import i", True),
        ("from a.b.a import i", ["a"], "from .b.a import i", True),
    ],
)
def test_simple_import(
    input_code: str, import_stmt: list[str], expected_code: str, expected_is_fixed: bool
):
    tokens = tokenize_rt.src_to_tokens(input_code)
    node = ast.parse(input_code).body[0]

    new_tokens, is_fixed = replace_tokens_2(tokens, node, import_stmt)

    assert is_fixed is expected_is_fixed
    assert tokenize_rt.tokens_to_src(new_tokens) == expected_code
