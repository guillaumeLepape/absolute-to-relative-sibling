import ast
from pathlib import Path
from typing import TYPE_CHECKING, List, Tuple

import tokenize_rt
from typer import Typer

from .git import find_project_root, get_gitignore

if TYPE_CHECKING:
    from pathspec import PathSpec

__version__ = "0.1.0"

app = Typer()


def read_file(path: Path) -> str:
    with path.open(mode="rb") as file:
        contents_bytes = file.read()

    return contents_bytes.decode()


def write_file(path: Path, contents_text: str) -> None:
    with path.open(mode="w", encoding="UTF-8", newline="") as file:
        file.write(contents_text)


def replace_tokens(python_file: Path) -> None:
    relative_to_module = ".".join(python_file.parts[:-1])

    contents_text = read_file(python_file)

    contents_text, is_fixed = replace_tokens_file(contents_text, python_file, relative_to_module)

    if is_fixed is True:
        write_file(python_file, contents_text)


def replace_tokens_file(
    contents_text: str, python_file: Path, relative_to_module: str
) -> Tuple[str, bool]:
    is_fixed = False
    file_ast = ast.parse(contents_text)
    tokens = tokenize_rt.src_to_tokens(contents_text)

    for node in file_ast.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.module is not None
            and node.module.startswith(f"{relative_to_module}.")
        ):
            print(python_file, node.lineno)
            print(
                "Can be replace by: from"
                f" {node.module.replace(relative_to_module, '')} import"
                f" {', '.join(i.name for i in node.names)}"
            )

            import_stmt = relative_to_module.split(".")

            tokens, is_fixed = replace_tokens_import(tokens, node, import_stmt)

    return tokenize_rt.tokens_to_src(tokens), is_fixed


def replace_tokens_import(
    tokens: List[tokenize_rt.Token], node: ast.ImportFrom, import_stmt: List[str]
) -> Tuple[List[tokenize_rt.Token], bool]:
    is_fixed = False

    new_tokens: List[tokenize_rt.Token] = []

    remove_op_dot = False

    new_tokens: List[tokenize_rt.Token] = []

    for token in tokens:
        if remove_op_dot is True:
            remove_op_dot = False
        elif token.name == "NAME" and token.src in import_stmt and token.line == node.lineno:
            is_fixed = True
            if token.src != import_stmt[-1] or import_stmt.count(token.src) > 1:
                remove_op_dot = True
            import_stmt.remove(token.src)
        else:
            new_tokens.append(token)

    return new_tokens, is_fixed


def format_file(filename: Path, root: Path, gitignore: "PathSpec") -> None:
    if gitignore.match_file(filename.relative_to(root)):
        return
    replace_tokens(filename)


def iterate_files(srcs: List[Path], gitignore: "PathSpec", root: Path):
    for file_or_dir in srcs:
        if file_or_dir.is_dir():
            for python_file in file_or_dir.glob("**/*.py"):
                format_file(python_file, root, gitignore)
        elif file_or_dir.is_file():
            format_file(file_or_dir, root, gitignore)
        else:
            msg = f"{file_or_dir} must be a directory or file"
            raise ValueError(msg)


def main(srcs: List[Path]):
    for file_or_dir in srcs:
        if not file_or_dir.exists():
            msg = f"{file_or_dir} does not exist"
            raise ValueError(msg)

    root, _ = find_project_root(srcs)

    print(root)

    gitignore = get_gitignore(root)

    srcs = [Path(src).resolve() for src in srcs]

    iterate_files(srcs, gitignore, root)


app.command()(main)


if __name__ == "__main__":
    app()
