from pathlib import Path
from typing import List, Sequence, Tuple

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


def find_project_root(srcs: Sequence[str]) -> Tuple[Path, str]:
    """Return a directory containing .git, .hg, or pyproject.toml.

    That directory will be a common parent of all files and directories
    passed in `srcs`.

    If no directory in the tree contains a marker that would specify it's the
    project root, the root of the file system is returned.

    Returns a two-tuple with the first element as the project root path and
    the second element as a string describing the method by which the
    project root was discovered.
    """
    if not srcs:
        srcs = [str(Path.cwd().resolve())]

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
            return directory, ".git directory"

        if (directory / ".hg").is_dir():
            return directory, ".hg directory"

        if (directory / "pyproject.toml").is_file():
            return directory, "pyproject.toml"

    return directory.resolve(), "file system root"
