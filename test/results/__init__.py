# Adapted from https://github.com/mikf/gallery-dl/blob/master/test/results/__init__.py

import functools
from pathlib import Path

__directory__ = Path(__file__).parent


@functools.lru_cache(maxsize=None)
def tests(name):
    module = __import__(name, globals(), None, (), 1)
    return module.__tests__


def all():
    ignore = {"__init__.py", "__pycache__"}
    for filepath in __directory__.iterdir():
        if filepath.name not in ignore and filepath.suffix == ".py":
            yield from tests(filepath.stem)


def category(category):
    return tests(category.replace(".", ""))
