from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from absolute_to_relative_sibling import app

from .utils import setup_app

if TYPE_CHECKING:
    from typer.testing import CliRunner


def test_git_ignore_directory(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        setup_app()

        Path(".gitignore").write_text("foo/baz.py\n")

        result = runner.invoke(app, ["."])

        assert result.exit_code == 0
        assert not result.stdout
        assert (
            Path("foo", "baz.py").read_text()
            == "from foo.toto import a\nfrom foo.toto import b as alias_b\n"
        )


def test_git_ignore_file(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        setup_app()

        Path(".gitignore").write_text("foo/baz.py\n")

        result = runner.invoke(app, ["foo/bar.py", "foo/baz.py"])

        assert result.exit_code == 0
        assert not result.stdout
        assert (
            Path("foo", "baz.py").read_text()
            == "from foo.toto import a\nfrom foo.toto import b as alias_b\n"
        )


def test_invalid_git_ignore_format(runner: CliRunner) -> None:
    with runner.isolated_filesystem():
        setup_app()

        Path(".gitignore").write_text("!")

        result = runner.invoke(app, ["foo/baz.py"])

        assert result.exit_code == 1
        assert not result.stdout
        assert isinstance(result.exception, ValueError) is True
        assert re.match(
            r"Could not parse .+\.gitignore: Invalid git pattern: '!'",
            str(result.exception),
        )
