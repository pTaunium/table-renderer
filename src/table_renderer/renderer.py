import os
from typing import TYPE_CHECKING

from jinja2 import Template
from weasyprint import HTML

if TYPE_CHECKING:
    from .models.table import Table

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
@page {
    size: {{ page_width }}px {{ page_height }}px; /* Dynamically estimated size */
    margin: 0;
}
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


def render_to_html(table: "Table", *, background_color: str = "transparent") -> str:
    """
    Generate the HTML representation of the table.

    Args:
        table: The Table object to render.
        background_color: The background color of the body.

    Returns:
        A string containing the complete HTML document.
    """
    table._prepare_render()

    # Calculate final styles for each cell based on inheritance
    font_faces = []
    for font_path in table.font_files:
        name = os.path.splitext(os.path.basename(font_path))[0]
        # Convert path to absolute file URL for WeasyPrint
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

    # Estimate safe canvas width to prevent clipping
    # Base it on the number of columns if explicit widths aren't provided (assume ~100px min per column)
    col_count = len(table._cells[0]) if table._cells else 0
    estimated_width = max(2000, col_count * 100)

    if isinstance(table.width, int):
        estimated_width = max(estimated_width, table.width + 100)

    col_width_sum = 0
    for c in table._col_objects:
        if isinstance(c.width, int):
            col_width_sum += c.width
    estimated_width = max(estimated_width, col_width_sum + 100)

    # Estimate safe canvas height to optimize rendering speed for small tables, capped at 5000px
    # Assume a generous average of 40px per row plus 100px padding
    estimated_height = len(table._cells) * 40 + 100
    estimated_height = min(max(estimated_height, 500), 5000)

    template = Template(HTML_TEMPLATE)
    return template.render(
        page_width=estimated_width,
        page_height=estimated_height,
        background_color=background_color,
        table_width=f"{table.width}px" if isinstance(table.width, int) else table.width,
        table_style=table.style.to_css(),
        font_faces=font_faces,
        columns=[
            {
                "index": c.index,
                "width": f"{c.width}px" if isinstance(c.width, int) else c.width,
                "style": c.style.to_css(),
            }
            for c in table._col_objects
        ],
        rows=[
            {"index": r.index, "style": r.style.to_css()} for r in table._row_objects
        ],
        cells=cells_data,
    )


def render_to_image(
    table: "Table",
    output_path: str,
    *,
    dpi: int = 144,
    padding: int = 10,
    background_color: str = "transparent",
) -> None:
    """
    Render the table to an image file.

    Args:
        table: The Table object to render.
        output_path: Destination path for the image.
        dpi: Target resolution.
        padding: Margin around the table.
        background_color: Background color of the image.
    """
    html_content = render_to_html(table, background_color=background_color)
    # WeasyPrint v53+ removed write_png, so we render to PDF then convert to PNG
    pdf_bytes = HTML(string=html_content).write_pdf()

    import pypdfium2 as pdfium
    from PIL import Image

    # Load the PDF from bytes
    with pdfium.PdfDocument(pdf_bytes) as pdf:
        page_images = []
        scale_factor = dpi / 72

        # Render each page to a PIL Image
        for page in pdf:
            # fill_color=(255, 255, 255, 0) ensures the background is transparent
            bitmap = page.render(scale=scale_factor, fill_color=(255, 255, 255, 0))
            pil_page = bitmap.to_pil()
            page_images.append(pil_page)
            bitmap.close()

        if not page_images:
            return

        # Stitch all pages vertically into one long image
        total_width = max(img.width for img in page_images)
        total_height = sum(img.height for img in page_images)

        # Create a large canvas
        pil_image = Image.new("RGBA", (total_width, total_height), (255, 255, 255, 0))
        y_offset = 0
        for img in page_images:
            pil_image.paste(img, (0, y_offset))
            y_offset += img.height

    # Visual Auto-Crop: Find the bounding box of non-white pixels
    # Use 'L' (grayscale) mode to reduce memory usage (1 byte per pixel vs 3)
    if pil_image.mode == "RGBA":
        # Flatten RGBA onto a white grayscale background
        grayscale = Image.new("L", pil_image.size, 255)
        grayscale.paste(pil_image.convert("L"), mask=pil_image.getchannel("A"))
    else:
        # For RGB or other modes, just convert to grayscale
        grayscale = pil_image.convert("L")

    # Invert and find bbox of "ink" (non-white pixels)
    import PIL.ImageOps

    inverted = PIL.ImageOps.invert(grayscale)
    bbox = inverted.getbbox()

    if bbox:
        # Add some padding
        left, top, right, bottom = bbox
        left = max(0, left - padding)
        top = max(0, top - padding)
        right = min(pil_image.width, right + padding)
        bottom = min(pil_image.height, bottom + padding)
        pil_image = pil_image.crop((left, top, right, bottom))

    # Save to the requested format (Pillow handles most formats)
    if output_path.lower().endswith((".jpg", ".jpeg")) and pil_image.mode == "RGBA":
        # Create a white background image and paste the RGBA image on it to flatten it
        rgb_image = Image.new("RGB", pil_image.size, (255, 255, 255))
        rgb_image.paste(pil_image, mask=pil_image.split()[3])
        pil_image = rgb_image

    pil_image.save(output_path)


def save_html(
    table: "Table", output_path: str, *, background_color: str = "transparent"
) -> None:
    """
    Save the table's HTML representation to a file.

    Args:
        table: The Table object to export.
        output_path: Path to the destination HTML file.
        background_color: Background color of the HTML body.
    """
    html_content = render_to_html(table, background_color=background_color)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
