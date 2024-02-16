import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from typer import Typer

from .git import find_project_root, get_gitignore

__version__ = "0.1.0"

app = Typer()


def read_file(path: Path) -> str:
    with path.open(mode="rb") as file:
        contents_bytes = file.read()

    return contents_bytes.decode()


def check_file(python_file: Path) -> None:
    parts = list(python_file.resolve().parts[:-1])

    contents_text = read_file(python_file)

    issues = detect_issues(contents_text, python_file, parts)

    for issue in issues:
        print(f"{issue.file}:{issue.line} - {issue.message}")


@dataclass
class Issue:
    file: Path
    line: int
    message: str


def unparse_alias(alias: ast.alias) -> str:
    if alias.asname is None:
        return alias.name

    return f"{alias.name} as {alias.asname}"


def unparse_import_from(node: ast.ImportFrom) -> str:
    return (
        f"from {'.' * node.level}{node.module} "
        f"import {', '.join(unparse_alias(alias) for alias in node.names)}"
    )


def detect_issues(contents_text: str, python_file: Path, parts: List[str]) -> List[Issue]:
    file_ast = ast.parse(contents_text)

    result: List[Issue] = []

    for node in file_ast.body:
        if isinstance(node, ast.ImportFrom) and node.module is not None and node.level == 0:
            if "." in node.module:
                names = node.module.split(".")
            else:
                names = [node.module]

            level: Optional[int] = None

            for i in range(min(len(parts), len(names)) + 1):
                if parts[-i:] == names[:i]:
                    level = i

            if level is not None:
                node.level = 1
                node.module = ".".join(names[level:])

                result.append(
                    Issue(
                        file=python_file,
                        line=node.lineno,
                        message=f"rewrite as: {unparse_import_from(node)}",
                    )
                )

    return result


def main(file_or_dirs: List[Path]):
    for file_or_dir in file_or_dirs:
        if not file_or_dir.exists():
            msg = f"{file_or_dir} does not exist"
            raise ValueError(msg)

    root_dir = find_project_root(file_or_dirs)

    gitignore = get_gitignore(root_dir)

    for file_or_dir in file_or_dirs:
        if file_or_dir.is_dir():
            for python_file in file_or_dir.glob("**/*.py"):
                if gitignore.match_file(python_file.resolve().relative_to(root_dir)):
                    continue
                check_file(python_file)
        elif file_or_dir.is_file():
            if gitignore.match_file(file_or_dir.resolve().relative_to(root_dir)):
                continue
            check_file(file_or_dir)
        else:
            msg = f"{file_or_dir} must be a directory or file"
            raise ValueError(msg)


app.command()(main)


if __name__ == "__main__":
    app()
