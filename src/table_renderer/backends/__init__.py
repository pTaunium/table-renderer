"""Rendering backends for table-renderer."""

from .base import ImageRenderer
from .weasyprint_renderer import WeasyPrintRenderer

__all__ = ["ImageRenderer", "WeasyPrintRenderer"]
