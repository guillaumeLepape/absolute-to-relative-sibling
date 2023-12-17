from pathlib import Path


def setup_app():
    Path("foo").mkdir()
    Path("foo", "__init__.py").write_text("")
    Path("foo", "bar.py").write_text("a = 1\nb = 2*a")
    Path("foo", "baz.py").write_text("from foo.toto import a\nfrom foo.toto import b as alias_b\n")
