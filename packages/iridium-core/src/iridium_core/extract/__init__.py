"""Extractor plugins."""

from iridium_core.extract.base import ImportMap, LanguageExtractor
from iridium_core.extract.javascript_extractor import JavaScriptExtractor
from iridium_core.extract.python_extractor import PythonExtractor

__all__ = [
    "ImportMap",
    "JavaScriptExtractor",
    "LanguageExtractor",
    "PythonExtractor",
]

DEFAULT_EXTRACTORS: list[LanguageExtractor] = [
    PythonExtractor(),
    JavaScriptExtractor(),
]
