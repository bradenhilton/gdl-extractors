# Adapted from https://github.com/mikf/gallery-dl/blob/master/gallery_dl/extractor/__init__.py

import re
import sys
from pathlib import Path

__dirname__ = Path(__file__).parent

ignore = {"__init__.py", "__pycache__"}
modules = [
    filepath.stem for filepath in __dirname__.iterdir() if filepath.name not in ignore and filepath.suffix == ".py"
]


def find(url):
    """Find a suitable extractor for the given URL"""
    for cls in _list_classes():
        match = cls.pattern.match(url)
        if match:
            return cls(match)
    return None


def add(cls):
    """Add 'cls' to the list of available extractors"""
    cls.pattern = re.compile(cls.pattern)
    _cache.append(cls)
    return cls


def add_module(module):
    """Add all extractors in 'module' to the list of available extractors"""
    classes = _get_classes(module)
    for cls in classes:
        cls.pattern = re.compile(cls.pattern)
    _cache.extend(classes)
    return classes


def extractors():
    """Yield all available extractor classes"""
    return sorted(_list_classes(), key=lambda x: x.__name__)


# --------------------------------------------------------------------
# internals


def _list_classes():
    """Yield available extractor classes"""
    yield from _cache

    for module in _module_iter:
        yield from add_module(module)

    globals()["_list_classes"] = lambda: _cache


def _modules_internal():
    globals_ = globals()
    for module_name in modules:
        yield __import__(module_name, globals_, None, (), 1)


def _modules_path(path, files):
    sys.path.insert(0, path)
    try:
        return [__import__(name[:-3]) for name in files if name.endswith(".py")]
    finally:
        del sys.path[0]


def _get_classes(module):
    """Return a list of all extractor classes in a module"""
    return [cls for cls in module.__dict__.values() if (hasattr(cls, "pattern") and cls.__module__ == module.__name__)]


_cache = []
_module_iter = _modules_internal()
