from __future__ import annotations

import argparse
import ast
from pathlib import Path

import tokenize_rt

__version__ = "0.1.0"


def introspect_python_modules(root_path: Path) -> list[str]:
    return [
        path.name
        for path in root_path.glob("*")
        if path.is_dir() and (path / "__init__.py").exists()
    ]


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
) -> tuple[str, bool]:
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
    tokens: list[tokenize_rt.Token], node: ast.ImportFrom, import_stmt: list[str]
) -> tuple[list[tokenize_rt.Token], bool]:
    is_fixed = False

    new_tokens: list[tokenize_rt.Token] = []

    remove_op_dot = False

    new_tokens: list[tokenize_rt.Token] = []

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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file_or_dirs", nargs="+", type=Path)

    args = parser.parse_args()

    for file_or_dir in args.file_or_dirs:
        if not file_or_dir.exists():
            msg = f"{file_or_dir} does not exist"
            raise ValueError(msg)

    for file_or_dir in args.file_or_dirs:
        if file_or_dir.is_dir():
            for python_file in file_or_dir.glob("**/*.py"):
                replace_tokens(python_file)
        elif file_or_dir.is_file():
            replace_tokens(file_or_dir)
        else:
            msg = f"{file_or_dir} must be a directory or file"
            raise ValueError(msg)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
