"""HTML generation from Table models.

This module converts Table data models into HTML document strings.
It provides shared utilities that rendering backends can use, but
is not tied to any specific rendering engine.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from jinja2 import Environment, FileSystemLoader, Template

if TYPE_CHECKING:
    from .models.table import Table

# HTML template loaded from templates/table.html.j2
_JINJA_ENV: Environment | None = None


def _get_template() -> Template:
    """Return the cached Jinja2 table template, initializing the environment on first call."""
    global _JINJA_ENV
    if _JINJA_ENV is None:
        template_dir = Path(__file__).parent / "templates"
        _JINJA_ENV = Environment(loader=FileSystemLoader(template_dir))  # noqa: S701
    return _JINJA_ENV.get_template("table.html.j2")


def _format_length(value: int | str) -> str:
    """Format an integer as pixels, or return a string CSS value as is."""
    return f"{value}px" if isinstance(value, int) else value


def _prepare_render_context(
    table: Table, *, background_color: str = "transparent"
) -> dict[str, Any]:
    """Prepare the Jinja2 template context from a Table model.

    Handles merge-flag setup, font-face resolution, image URL
    resolution, and extraction of column/row/cell data.

    Args:
        table: The Table object to prepare.
        background_color: The background color of the body.

    Returns:
        A dict suitable for passing to ``Template.render()``.
    """
    table._prepare_render()

    font_faces = []
    for font_path in table.font_files:
        font_name = os.path.splitext(os.path.basename(font_path))[0]
        # Convert path to absolute file URL for rendering engines
        absolute_font_path = os.path.abspath(font_path)
        font_faces.append({"name": font_name, "path": f"file://{absolute_font_path}"})

    cell_matrix = []
    for row_index in range(len(table._cells)):
        cell_row = []
        for col_index in range(len(table._cells[0])):
            cell = table._cells[row_index][col_index]

            # Handle Image URL resolution
            cell.image_url = ""
            if cell.image_path:
                if cell.image_path.startswith(("http://", "https://")):
                    cell.image_url = cell.image_path
                else:
                    absolute_image_path = os.path.abspath(cell.image_path)
                    cell.image_url = f"file://{absolute_image_path}"

            cell_row.append(cell)
        cell_matrix.append(cell_row)

    return {
        "background_color": background_color,
        "table_width": _format_length(table.width),
        "table_style": table.style.to_css(),
        "font_faces": font_faces,
        "columns": [
            {
                "index": c.index,
                "width": _format_length(c.width),
                "style": c.style.to_css(),
            }
            for c in table._col_objects
        ],
        "rows": [
            {
                "index": r.index,
                "height": _format_length(r.height),
                "style": r.style.to_css(),
            }
            for r in table._row_objects
        ],
        "cells": cell_matrix,
    }


def render_to_html(
    table: Table,
    *,
    background_color: str = "transparent",
    extra_css: str = "",
) -> str:
    """Generate the HTML representation of the table.

    Args:
        table: The Table object to render.
        background_color: The background color of the body.
        extra_css: Additional CSS to inject into the document head.
            Used by backends to add engine-specific rules
            (e.g., ``@page`` rules for WeasyPrint).

    Returns:
        A string containing the complete HTML document.
    """
    context = _prepare_render_context(table, background_color=background_color)
    context["extra_css"] = extra_css
    template = _get_template()

    return template.render(**context)
