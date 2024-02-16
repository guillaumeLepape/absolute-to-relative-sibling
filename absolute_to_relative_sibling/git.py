from __future__ import annotations

from pathlib import Path
from typing import Sequence

from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPatternError


def get_gitignore(root: Path) -> PathSpec:
    """Return a PathSpec matching gitignore content if present."""
    gitignore = root / ".gitignore"

    lines: list[str] = []

    if gitignore.is_file():
        with gitignore.open(encoding="utf-8") as gf:
            lines = gf.readlines()

    try:
        return PathSpec.from_lines("gitwildmatch", lines)
    except GitWildMatchPatternError as e:
        msg = f"Could not parse {gitignore}: {e}"
        raise ValueError(msg) from e


def find_project_root(srcs: Sequence[Path]) -> Path:
    if not srcs:
        srcs = [Path.cwd().resolve()]

    path_srcs = [Path(Path.cwd(), src).resolve() for src in srcs]

    # A list of lists of parents for each 'src'. 'src' is included as a
    # "parent" of itself if it is a directory
    src_parents = [list(path.parents) + ([path] if path.is_dir() else []) for path in path_srcs]

    common_base = max(
        set.intersection(*(set(parents) for parents in src_parents)),
        key=lambda path: path.parts,
    )

    for directory in (common_base, *common_base.parents):
        if (directory / ".git").exists():
            return directory

        if (directory / ".hg").is_dir():
            return directory

        if (directory / "pyproject.toml").is_file():
            return directory

    return directory
