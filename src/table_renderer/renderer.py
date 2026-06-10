"""High-level rendering facade.

Orchestrates HTML generation, image rendering, and post-processing.
This module maintains backward compatibility with existing import
paths — all public function signatures are unchanged.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from table_renderer.backends.base import ImageRenderer
from table_renderer.backends.weasyprint_renderer import WeasyPrintRenderer

from .html_generator import estimate_page_css
from .html_generator import render_to_html as _generate_html

if TYPE_CHECKING:
    from PIL.Image import Image

    from .models.table import Table

# Default backend instance (lazily created or just instantiated)
_DEFAULT_RENDERER: ImageRenderer | None = None


def _get_default_renderer() -> ImageRenderer:
    global _DEFAULT_RENDERER
    if _DEFAULT_RENDERER is None:
        _DEFAULT_RENDERER = WeasyPrintRenderer()
    return _DEFAULT_RENDERER


def render_to_html(table: Table, *, background_color: str = "transparent") -> str:
    """Generate the HTML representation of the table.

    Args:
        table: The Table object to render.
        background_color: The background color of the body.

    Returns:
        A string containing the complete HTML document.
    """
    page_css = estimate_page_css(table)
    return _generate_html(table, background_color=background_color, extra_css=page_css)


def render_to_image(
    table: Table,
    output_path: str,
    *,
    dpi: int = 144,
    padding: int = 10,
    background_color: str = "transparent",
    renderer: ImageRenderer | None = None,
) -> None:
    """Render the table to an image file.

    Args:
        table: The Table object to render.
        output_path: Destination path for the image.
        dpi: Target resolution.
        padding: Margin around the table.
        background_color: Background color of the image.
        renderer: Optional custom rendering backend. Defaults to WeasyPrint.
    """
    renderer = renderer or _get_default_renderer()
    image = renderer.render(
        table, dpi=dpi, padding=padding, background_color=background_color
    )
    _save_image(image, output_path)


def save_html(
    table: Table, output_path: str, *, background_color: str = "transparent"
) -> None:
    """Save the table's HTML representation to a file.

    Args:
        table: The Table object to export.
        output_path: Path to the destination HTML file.
        background_color: Background color of the HTML body.
    """
    html_content = render_to_html(table, background_color=background_color)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)


def _save_image(image: Image, output_path: str) -> None:
    """Handle format-specific saving (e.g., JPG alpha flattening).

    Args:
        image: A PIL Image to save.
        output_path: Destination file path (format inferred from extension).
    """
    from PIL import Image

    if output_path.lower().endswith((".jpg", ".jpeg")) and image.mode == "RGBA":
        rgb_image = Image.new("RGB", image.size, (255, 255, 255))
        rgb_image.paste(image, mask=image.split()[3])
        image = rgb_image

    image.save(output_path)
