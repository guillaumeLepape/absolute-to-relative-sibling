from pathlib import Path
from typing import List

from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPatternError


def get_gitignore(root: Path) -> PathSpec:
    """Return a PathSpec matching gitignore content if present."""
    gitignore = root / ".gitignore"

    lines: List[str] = []

    if gitignore.is_file():
        with gitignore.open(encoding="utf-8") as gf:
            lines = gf.readlines()

    try:
        return PathSpec.from_lines("gitwildmatch", lines)
    except GitWildMatchPatternError as e:
        msg = f"Could not parse {gitignore}: {e}"
        raise ValueError(msg) from e
