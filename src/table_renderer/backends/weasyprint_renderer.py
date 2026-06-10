"""WeasyPrint-based rendering backend."""

from __future__ import annotations

from typing import TYPE_CHECKING

from weasyprint import HTML

from table_renderer.html_generator import render_to_html

if TYPE_CHECKING:
    from PIL.Image import Image

    from table_renderer.models.cell import Cell
    from table_renderer.models.table import Table

_DEFAULT_COL_WIDTH = 100
_DEFAULT_FONT_SIZE = 16
_CELL_PADDING = 8
_LINE_HEIGHT_RATIO = 1.4
_MIN_PAGE_WIDTH = 200
_MIN_PAGE_HEIGHT = 200
_PAGE_PADDING = 60  # body padding (20px * 2) + safety margin


class WeasyPrintRenderer:
    """Renders tables via WeasyPrint (HTML → PDF → raster image).

    This is the default rendering backend. It converts HTML to PDF
    via WeasyPrint, rasterizes the PDF pages to bitmaps via pypdfium2,
    and auto-crops excess whitespace from the PDF page.
    """

    def render(
        self,
        table: Table,
        *,
        dpi: int = 144,
        padding: int = 10,
        background_color: str = "transparent",
    ) -> Image:
        """Render a Table to a tightly-cropped PIL Image.

        Args:
            table: The Table data model to render.
            dpi: Target resolution in dots per inch.
            padding: Pixels of padding around content.
            background_color: Background color.

        Returns:
            A PIL Image (RGBA mode) tightly cropped to the table.
        """
        page_css = _estimate_page_css(table)
        html = render_to_html(
            table, background_color=background_color, extra_css=page_css
        )

        # WeasyPrint v53+ removed write_png, so we render to PDF then convert
        pdf_bytes = HTML(string=html).write_pdf()
        raw_image = _pdf_to_image(pdf_bytes, dpi=dpi)
        return _auto_crop(raw_image, padding=padding)


def _estimate_page_css(table: Table) -> str:
    """Generate ``@page`` CSS rules with estimated canvas size.

    Estimates the PDF page dimensions based on the actual table
    content — column widths, font sizes, text line counts, and
    embedded image heights — rather than fixed magic numbers.

    Args:
        table: The Table object to estimate dimensions for.

    Returns:
        A CSS string containing the ``@page`` rule.
    """
    estimated_width = _estimate_width(table)
    estimated_height = _estimate_height(table)

    return (
        "@page {\n"
        f"    size: {estimated_width}px {estimated_height}px;"
        " /* Dynamically estimated size */\n"
        "    margin: 0;\n"
        "}"
    )


def _estimate_width(table: Table) -> int:
    """Estimate the required page width in pixels.

    Uses explicit column widths where available and falls back
    to a default per-column width for unset columns.

    Args:
        table: The Table to estimate width for.

    Returns:
        Estimated width in pixels.
    """
    if not table._cells:
        return _MIN_PAGE_WIDTH

    # If the table has an explicit pixel width, use it directly
    if isinstance(table.width, int):
        return max(_MIN_PAGE_WIDTH, table.width + _PAGE_PADDING)

    # Sum column widths: use explicit value or default
    total = 0
    for col in table._col_objects:
        if isinstance(col.width, int):
            total += col.width
        else:
            total += _DEFAULT_COL_WIDTH

    return max(_MIN_PAGE_WIDTH, total + _PAGE_PADDING)


def _estimate_height(table: Table) -> int:
    """Estimate the required page height in pixels.

    Calculates a per-row height based on the tallest cell in
    each row, considering font size, number of text lines, and
    embedded image height.

    Args:
        table: The Table to estimate height for.

    Returns:
        Estimated height in pixels.
    """
    if not table._cells:
        return _MIN_PAGE_HEIGHT

    # Resolve the table-level default font size
    table_font_size = table.style.font_size or _DEFAULT_FONT_SIZE

    total_height = 0
    for row_idx, row_cells in enumerate(table._cells):
        # Resolve row-level font size
        row_font_size = table._row_objects[row_idx].style.font_size or table_font_size

        row_height = 0
        for cell in row_cells:
            if cell.is_merged:
                continue

            cell_height = _estimate_cell_height(cell, default_font_size=row_font_size)
            row_height = max(row_height, cell_height)

        total_height += row_height

    return max(_MIN_PAGE_HEIGHT, total_height + _PAGE_PADDING)


def _estimate_cell_height(cell: Cell, *, default_font_size: int) -> int:
    """Estimate the height of a single cell in pixels.

    Accounts for font size, number of text lines (split by newlines),
    cell padding, and embedded image height.

    Args:
        cell: The Cell to estimate.
        default_font_size: Inherited font size if the cell has none set.

    Returns:
        Estimated cell height in pixels.
    """
    font_size = cell.style.font_size or default_font_size

    # Text height: number of lines * font_size * line-height + padding
    line_count = max(1, cell.value.count("\n") + 1) if cell.value else 1
    text_height = int(line_count * font_size * _LINE_HEIGHT_RATIO) + _CELL_PADDING * 2

    # Image height (if present)
    image_height = (cell.image_height or 0) + (_CELL_PADDING if cell.image_path else 0)

    return text_height + image_height


def _pdf_to_image(pdf_bytes: bytes, *, dpi: int) -> Image:
    """Convert PDF bytes to a single stitched PIL Image.

    Renders each page of the PDF at the specified DPI and
    stitches them vertically into one tall image.

    Args:
        pdf_bytes: Raw PDF bytes.
        dpi: Target resolution in dots per inch.

    Returns:
        A PIL RGBA Image with all pages stitched vertically.
    """
    import pypdfium2 as pdfium
    from PIL import Image

    with pdfium.PdfDocument(pdf_bytes) as pdf:
        page_images = []
        scale_factor = dpi / 72

        # Render each page to a PIL Image
        for page in pdf:
            # fill_color=(255, 255, 255, 0) ensures transparent background
            bitmap = page.render(scale=scale_factor, fill_color=(255, 255, 255, 0))
            pil_page = bitmap.to_pil()
            page_images.append(pil_page)
            bitmap.close()

        if not page_images:
            return Image.new("RGBA", (1, 1), (255, 255, 255, 0))

        # Stitch all pages vertically into one long image
        total_width = max(img.width for img in page_images)
        total_height = sum(img.height for img in page_images)
        result = Image.new("RGBA", (total_width, total_height), (255, 255, 255, 0))

        y_offset = 0
        for img in page_images:
            result.paste(img, (0, y_offset))
            y_offset += img.height

    return result


def _auto_crop(image: Image, *, padding: int) -> Image:
    """Crop excess PDF page whitespace around the table.

    WeasyPrint renders to a full PDF page, so the rendered image
    typically has large margins that need to be trimmed.

    Args:
        image: The source PIL Image.
        padding: Pixels of padding to preserve around content.

    Returns:
        The cropped image.
    """
    import PIL.ImageOps
    from PIL import Image

    # Visual Auto-Crop: Find the bounding box of non-white pixels
    # Use 'L' (grayscale) mode to reduce memory usage (1 byte per pixel vs 3)
    if image.mode == "RGBA":
        # Flatten RGBA onto a white grayscale background
        grayscale = Image.new("L", image.size, 255)
        grayscale.paste(image.convert("L"), mask=image.getchannel("A"))
    else:
        # For RGB or other modes, just convert to grayscale
        grayscale = image.convert("L")

    # Invert and find bbox of "ink" (non-white pixels)
    inverted = PIL.ImageOps.invert(grayscale)
    bbox = inverted.getbbox()

    if bbox:
        # Add some padding
        left, top, right, bottom = bbox
        left = max(0, left - padding)
        top = max(0, top - padding)
        right = min(image.width, right + padding)
        bottom = min(image.height, bottom + padding)
        image = image.crop((left, top, right, bottom))

    return image
