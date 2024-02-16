from __future__ import annotations

import os
import socket
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from absolute_to_relative_sibling import app

from .utils import setup_app

runner = CliRunner()


def test_cli_directory():
    with runner.isolated_filesystem():
        setup_app()

        result = runner.invoke(app, ["."])

        assert result.exit_code == 0
        assert result.stdout == (
            f"foo{os.sep}baz.py:1 - rewrite as: from .toto import a\n"
            f"foo{os.sep}baz.py:2 - rewrite as: from .toto import b as alias_b\n"
        )

        os.chdir("foo")

        result = runner.invoke(app, ["."])

        assert result.exit_code == 0
        assert result.stdout == (
            "baz.py:1 - rewrite as: from .toto import a\n"
            "baz.py:2 - rewrite as: from .toto import b as alias_b\n"
        )


def test_cli_file():
    with runner.isolated_filesystem():
        setup_app()
        result = runner.invoke(app, ["foo/baz.py"])

        assert result.exit_code == 0
        assert result.stdout == (
            f"foo{os.sep}baz.py:1 - rewrite as: from .toto import a\n"
            f"foo{os.sep}baz.py:2 - rewrite as: from .toto import b as alias_b\n"
        )


def test_file_not_exists():
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["not_exists.py"])

        assert result.exit_code == 1
        assert result.stdout == ""
        assert isinstance(result.exception, ValueError) is True
        assert str(result.exception) == "not_exists.py does not exist"


@pytest.mark.skipif(sys.platform != "linux", reason="Only for linux")
def test_socket_file():
    with runner.isolated_filesystem():
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.bind("./sock.py")

        result = runner.invoke(app, ["sock.py"])

        assert result.exit_code == 1
        assert result.stdout == ""
        assert isinstance(result.exception, ValueError) is True
        assert str(result.exception) == "sock.py must be a directory or file"


def test_parent_and_child_modules_with_same_name():
    """
    .
    ├── bar
    │   ├── __init__.py
    │   ├── bar.py
    │   └── foo.py
    └── pyproject.toml
    """

    with runner.isolated_filesystem():
        Path("bar").mkdir()
        Path("bar", "__init__.py").write_text("")
        Path("bar", "bar.py").write_text("a = 1")
        Path("bar", "foo.py").write_text("from .bar import a")
        Path("pyproject.toml").write_text("")

        result = runner.invoke(app, ["."])

        assert result.exit_code == 0
        assert result.stdout == ""
