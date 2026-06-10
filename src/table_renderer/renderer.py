"""High-level rendering facade.

Orchestrates HTML generation, image rendering, and post-processing.
Re-exports ``render_to_html`` from ``html_generator`` and delegates
image rendering to a pluggable ``ImageRenderer`` backend.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import deprecated

from .backends.base import ImageRenderer
from .backends.weasyprint_renderer import WeasyPrintRenderer
from .html_generator import render_to_html

if TYPE_CHECKING:
    from PIL.Image import Image

    from .models.table import Table

# Default backend instance, lazily initialized on first use.
_DEFAULT_RENDERER: ImageRenderer | None = None


def _get_default_renderer() -> ImageRenderer:
    """Return the default renderer, creating a WeasyPrintRenderer on first call."""
    global _DEFAULT_RENDERER
    if _DEFAULT_RENDERER is None:
        _DEFAULT_RENDERER = WeasyPrintRenderer()
    return _DEFAULT_RENDERER


def save_image(
    table: Table,
    output_path: str,
    *,
    dpi: int = 144,
    padding: int = 10,
    background_color: str = "transparent",
    renderer: ImageRenderer | None = None,
) -> None:
    """Render the table and save to an image file.

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
    _write_pil_image(image, output_path)


@deprecated("Use `save_image` instead.")
def render_to_image(
    table: Table,
    output_path: str,
    *,
    dpi: int = 144,
    padding: int = 10,
    background_color: str = "transparent",
    renderer: ImageRenderer | None = None,
) -> None:
    """Render the table and save to an image file.

    .. deprecated::
        Use :func:`save_image` instead.
    """
    import warnings

    warnings.warn(
        "render_to_image() is deprecated, use save_image() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    save_image(
        table,
        output_path,
        dpi=dpi,
        padding=padding,
        background_color=background_color,
        renderer=renderer,
    )


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


def _write_pil_image(image: Image, output_path: str) -> None:
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
