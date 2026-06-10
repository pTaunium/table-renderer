"""WeasyPrint-based rendering backend."""

from __future__ import annotations

from typing import TYPE_CHECKING

from weasyprint import HTML

from table_renderer.html_generator import estimate_page_css, render_to_html

if TYPE_CHECKING:
    from PIL.Image import Image

    from table_renderer.models.table import Table


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
        page_css = estimate_page_css(table)
        html = render_to_html(
            table, background_color=background_color, extra_css=page_css
        )

        # WeasyPrint v53+ removed write_png, so we render to PDF then convert
        pdf_bytes = HTML(string=html).write_pdf()
        raw_image = _pdf_to_image(pdf_bytes, dpi=dpi)
        return _auto_crop(raw_image, padding=padding)


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
