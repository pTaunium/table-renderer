from typing import Self

from typing_extensions import deprecated

from .style import StyledObject


class Cell(StyledObject):
    """Represents a single cell in a table."""

    def __init__(self, value: str = "") -> None:
        """
        Initialize cell with a value.

        Args:
            value: The text content of the cell.
        """
        super().__init__()
        self.value = value
        self.row_span = 1
        self.col_span = 1
        self.is_merged = False  # If True, this cell is covered by another merged cell
        self.final_style: str = ""
        self.image_path: str | None = None
        self.image_url: str = ""
        self.image_width: int | None = None
        self.image_height: int | None = None

    def set_text(self, text: str) -> Self:
        """
        Update the text content of the cell.

        Args:
            text: New text content.

        Returns:
            The cell itself for chaining.
        """
        self.value = text
        return self

    def set_image(
        self, path: str, *, width: int | None = None, height: int | None = None
    ) -> Self:
        """
        Set an image to be displayed in the cell.

        Args:
            path: Path to the image file.
            width: Optional display width in pixels.
            height: Optional display height in pixels.

        Returns:
            The cell itself for chaining.
        """
        self.image_path = path
        self.image_width = width
        self.image_height = height
        return self

    def set_span(self, *, rows: int = 1, cols: int = 1) -> Self:
        """Set the row and column span for merging.

        Args:
            rows: Number of rows to span.
            cols: Number of columns to span.

        Returns:
            The cell itself for chaining.
        """
        self.row_span = rows
        self.col_span = cols
        return self

    @deprecated("Use `set_span` instead.")
    def span(self, *, rows: int = 1, cols: int = 1) -> Self:
        """Set the row and column span for merging.

        .. deprecated::
            Use :meth:`set_span` instead.

        Args:
            rows: Number of rows to span.
            cols: Number of columns to span.

        Returns:
            The cell itself for chaining.
        """
        import warnings

        warnings.warn(
            "Cell.span() is deprecated, use Cell.set_span() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.set_span(rows=rows, cols=cols)
