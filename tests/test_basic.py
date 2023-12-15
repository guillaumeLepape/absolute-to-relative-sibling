from __future__ import annotations

from pathlib import Path

import pytest

from absolute_to_relative_sibling import replace_tokens_file


@pytest.mark.parametrize(
    "input_code,relative_to_module,expected_code,expected_is_fixed",
    [
        ("from i.j import a, b, c", "i", "from .j import a, b, c", True),
        (
            "from i.j import a, b as new_b, c as new_c",
            "i",
            "from .j import a, b as new_b, c as new_c",
            True,
        ),
        ("from a.b.a import i", "a.b", "from .a import i", True),
        ("from a.b.a import i", "a", "from .b.a import i", True),
        ("a = 1", "a", "a = 1", False),
        (
            "from mod1.submod import func\nfrom mod2.submod import func2",
            "mod1",
            "from .submod import func\nfrom mod2.submod import func2",
            True,
        ),
    ],
)
def test_simple_import(
    input_code: str, relative_to_module: str, expected_code: str, expected_is_fixed: bool
):
    output_code, is_fixed = replace_tokens_file(input_code, Path(), relative_to_module)

    assert is_fixed is expected_is_fixed
    assert output_code == expected_code
