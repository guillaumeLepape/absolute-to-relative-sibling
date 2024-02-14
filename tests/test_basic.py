from __future__ import annotations

from pathlib import Path

import pytest

from absolute_to_relative_sibling import Issue, detect_issues


@pytest.mark.parametrize(
    "input_code,relative_to_module,expected_issues",
    [
        (
            "from i.j import a, b, c",
            "i",
            [Issue(file=Path(), line=1, message="rewrite as: from .j import a, b, c")],
        ),
        (
            "from i.j import a, b as new_b, c as new_c",
            "i",
            [Issue(file=Path(), line=1, message="rewrite as: from .j import a, b, c")],
        ),
        (
            "from a.b.a import i",
            "a.b",
            [Issue(file=Path(), line=1, message="rewrite as: from .a import i")],
        ),
        (
            "from a.b.a import i",
            "a",
            [Issue(file=Path(), line=1, message="rewrite as: from .b. import i")],
        ),
        ("a = 1", "a", []),
        (
            "from mod1.submod import func\nfrom mod2.submod import func2",
            "mod1",
            [Issue(file=Path(), line=1, message="rewrite as: from .submod import func")],
        ),
    ],
)
def test_simple_import(input_code: str, relative_to_module: str, expected_issues: list[Issue]):
    assert detect_issues(input_code, Path(), relative_to_module) == expected_issues
