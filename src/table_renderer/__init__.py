import importlib.metadata

from .models import Cell, Column, Row, Style, StyledObject, Table

try:
    __version__ = importlib.metadata.version("table-renderer")
except importlib.metadata.PackageNotFoundError:
    # Package is not installed (e.g. during local development without pip install -e .)
    __version__ = "0.3.0"

__all__ = ["Cell", "Column", "Row", "Style", "StyledObject", "Table", "__version__"]
