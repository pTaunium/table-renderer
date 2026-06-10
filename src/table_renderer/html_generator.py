"""HTML generation from Table models.

This module converts Table data models into HTML document strings.
It provides shared utilities that rendering backends can use, but
is not tied to any specific rendering engine.

Key design decisions:
- The HTML template does NOT contain @page rules or other
  engine-specific CSS. Backends inject those via ``extra_css``.
- ``estimate_page_css()`` is provided as a utility for backends
  that need CSS Paged Media rules (e.g., WeasyPrint).
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from jinja2 import Template

if TYPE_CHECKING:
    from .models.table import Table

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
{{ extra_css }}
body {
    margin: 0;
    padding: 20px;
    background-color: {{ background_color }};
}
{% for font in font_faces %}
@font-face {
    font-family: '{{ font.name }}';
    src: url('{{ font.path }}');
}
{% endfor %}

table {
    border-collapse: collapse;
    width: {{ table_width }};
    {{ table_style }}
}

td {
    padding: 8px;
    box-sizing: border-box;
    {{ table_style }}
}

{% for col in columns %}
.col-{{ col.index }} {
    width: {{ col.width }};
    {{ col.style }}
}
{% endfor %}

{% for row in rows %}
.row-{{ row.index }} {
    {{ row.style }}
}
{% endfor %}
</style>
</head>
<body>
    <table>
        {% for r_idx in range(cells|length) %}
        <tr class="row-{{ r_idx }}">
            {% for c_idx in range(cells[r_idx]|length) %}
                {% set cell = cells[r_idx][c_idx] %}
                {% if not cell.is_merged %}
                <td class="row-{{ r_idx }} col-{{ c_idx }}"
                    rowspan="{{ cell.row_span }}"
                    colspan="{{ cell.col_span }}"
                    style="{{ cell.style.to_css() }}">
                    {% if cell.image_url %}
                    <img src="{{ cell.image_url }}"
                         style="{% if cell.image_width %}width: {{ cell.image_width }}px;{% endif %}
                                {% if cell.image_height %}height: {{ cell.image_height }}px;{% endif %}">
                    <br>
                    {% endif %}
                    {{ cell.value | replace('\\n', '<br>') }}
                </td>
                {% endif %}
            {% endfor %}
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""


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
        name = os.path.splitext(os.path.basename(font_path))[0]
        # Convert path to absolute file URL for rendering engines
        abs_path = os.path.abspath(font_path)
        font_faces.append({"name": name, "path": f"file://{abs_path}"})

    cells_data = []
    for row_index in range(len(table._cells)):
        row_data = []
        for col_index in range(len(table._cells[0])):
            cell = table._cells[row_index][col_index]

            # Handle Image URL resolution
            cell.image_url = ""
            if cell.image_path:
                if cell.image_path.startswith(("http://", "https://")):
                    cell.image_url = cell.image_path
                else:
                    abs_img_path = os.path.abspath(cell.image_path)
                    cell.image_url = f"file://{abs_img_path}"

            row_data.append(cell)
        cells_data.append(row_data)

    return {
        "background_color": background_color,
        "table_width": f"{table.width}px"
        if isinstance(table.width, int)
        else table.width,
        "table_style": table.style.to_css(),
        "font_faces": font_faces,
        "columns": [
            {
                "index": c.index,
                "width": f"{c.width}px" if isinstance(c.width, int) else c.width,
                "style": c.style.to_css(),
            }
            for c in table._col_objects
        ],
        "rows": [
            {"index": r.index, "style": r.style.to_css()} for r in table._row_objects
        ],
        "cells": cells_data,
    }


def estimate_page_css(table: Table) -> str:
    """Generate ``@page`` CSS rules with estimated canvas size.

    Produces ``@page`` rules for CSS Paged Media, primarily used by
    the WeasyPrint backend to set PDF page dimensions. The canvas
    size is estimated to be large enough to contain the table
    without clipping.

    Args:
        table: The Table object to estimate dimensions for.

    Returns:
        A CSS string containing the ``@page`` rule.
    """
    col_count = len(table._cells[0]) if table._cells else 0
    estimated_width = max(2000, col_count * 100)

    if isinstance(table.width, int):
        estimated_width = max(estimated_width, table.width + 100)

    col_width_sum = 0
    for c in table._col_objects:
        if isinstance(c.width, int):
            col_width_sum += c.width
    estimated_width = max(estimated_width, col_width_sum + 100)

    # Generous average of 40px per row plus 100px padding, capped at 5000px
    estimated_height = len(table._cells) * 40 + 100
    estimated_height = min(max(estimated_height, 500), 5000)

    return (
        "@page {\n"
        f"    size: {estimated_width}px {estimated_height}px;"
        " /* Dynamically estimated size */\n"
        "    margin: 0;\n"
        "}"
    )


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
    template = Template(HTML_TEMPLATE)
    return template.render(**context)
