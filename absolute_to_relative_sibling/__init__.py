import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List

from typer import Typer

from .git import get_gitignore

__version__ = "0.1.0"

app = Typer()


def read_file(path: Path) -> str:
    with path.open(mode="rb") as file:
        contents_bytes = file.read()

    return contents_bytes.decode()


def check_file(python_file: Path) -> None:
    relative_to_module = ".".join(python_file.parts[:-1])

    contents_text = read_file(python_file)

    issues = detect_issues(contents_text, python_file, relative_to_module)

    for issue in issues:
        print(f"{issue.file}:{issue.line} - {issue.message}")


@dataclass
class Issue:
    file: Path
    line: int
    message: str


def detect_issues(contents_text: str, python_file: Path, relative_to_module: str) -> List[Issue]:
    file_ast = ast.parse(contents_text)

    result: List[Issue] = []

    for node in file_ast.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.module is not None
            and node.module.startswith(f"{relative_to_module}.")
        ):
            result.append(
                Issue(
                    file=python_file,
                    line=node.lineno,
                    message="rewrite as: from"
                    f" {node.module.replace(relative_to_module, '')} import"
                    f" {', '.join(i.name for i in node.names)}",
                )
            )

    return result


def main(file_or_dirs: List[Path]):
    for file_or_dir in file_or_dirs:
        if not file_or_dir.exists():
            msg = f"{file_or_dir} does not exist"
            raise ValueError(msg)

    for file_or_dir in file_or_dirs:
        if file_or_dir.is_dir():
            for python_file in file_or_dir.glob("**/*.py"):
                if get_gitignore(Path()).match_file(python_file.relative_to(Path())):
                    continue
                check_file(python_file)
        elif file_or_dir.is_file():
            if get_gitignore(Path()).match_file(file_or_dir.relative_to(Path())):
                continue
            check_file(file_or_dir)
        else:
            msg = f"{file_or_dir} must be a directory or file"
            raise ValueError(msg)


app.command()(main)


if __name__ == "__main__":
    app()
