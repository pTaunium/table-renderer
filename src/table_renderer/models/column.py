from typing import Self

from .base import StyledObject


class Column(StyledObject):
    """Represents a column in a table."""

    def __init__(self, index: int) -> None:
        """
        Initialize a column.

        Args:
            index: The 0-based index of the column.
        """
        super().__init__()
        self.index = index
        self.width: int | str = "auto"

    def set_width(self, width: int | str) -> Self:
        """
        Set the width of the column.

        Args:
            width: Width in pixels (int) or CSS value (str, e.g., '10%').

        Returns:
            The column itself for chaining.
        """
        self.width = width
        return self
