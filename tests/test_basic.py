from __future__ import annotations

from pathlib import Path

import pytest

from absolute_to_relative_sibling import Issue, detect_issues


@pytest.mark.parametrize(
    "input_code,parts,expected_issues",
    [
        (
            "from i.j import a, b, c",
            ["i"],
            [Issue(file=Path(), line=1, message="rewrite as: from .j import a, b, c")],
        ),
        (
            "from i.j import a, b as new_b, c as new_c",
            ["i"],
            [
                Issue(
                    file=Path(),
                    line=1,
                    message="rewrite as: from .j import a, b as new_b, c as new_c",
                )
            ],
        ),
        (
            "from a.b.a import i",
            ["a", "b"],
            [Issue(file=Path(), line=1, message="rewrite as: from .a import i")],
        ),
        (
            "from a.b.a import i",
            ["a"],
            [Issue(file=Path(), line=1, message="rewrite as: from .b.a import i")],
        ),
        ("a = 1", ["a"], []),
        (
            "from mod1.submod import func\nfrom mod2.submod import func2",
            ["mod1"],
            [Issue(file=Path(), line=1, message="rewrite as: from .submod import func")],
        ),
        (
            (
                "from mod1.submod import func\n"
                "from mod2.submod import func2\n"
                "from mod1.submod import func3"
            ),
            ["mod1"],
            [
                Issue(file=Path(), line=1, message="rewrite as: from .submod import func"),
                Issue(file=Path(), line=3, message="rewrite as: from .submod import func3"),
            ],
        ),
    ],
)
def test_simple_import(input_code: str, parts: list[str], expected_issues: list[Issue]):
    assert detect_issues(input_code, Path(), parts) == expected_issues
