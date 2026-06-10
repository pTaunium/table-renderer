"""Protocol defining the image rendering backend interface."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from PIL.Image import Image

    from table_renderer.models.table import Table


class ImageRenderer(Protocol):
    """Interface for rendering a Table model to an image.

    All rendering backends must implement this interface. This allows
    swapping the underlying rendering engine (e.g., WeasyPrint, Blitz)
    without changing the public API or HTML generation logic.
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

        The returned image should be cropped to content bounds
        (plus the specified padding). It is the backend's
        responsibility to ensure no excess whitespace.

        Args:
            table: The Table data model to render.
            dpi: Target resolution in dots per inch.
            padding: Pixels of padding around content.
            background_color: Background color.

        Returns:
            A PIL Image (RGBA mode) tightly cropped to the table.
        """
        ...
