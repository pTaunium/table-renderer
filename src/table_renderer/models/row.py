from typing import Self

from .style import StyledObject


class Row(StyledObject):
    """Represents a row in a table."""

    def __init__(self, index: int) -> None:
        """
        Initialize a row.

        Args:
            index: The 0-based index of the row.
        """
        super().__init__()
        self.index = index
        self.height: int | str = "auto"

    def set_height(self, height: int | str) -> Self:
        """
        Set the height of the row.

        Args:
            height: Height in pixels (int) or CSS value (str, e.g., '50px', '2em').

        Returns:
            The row itself for chaining.
        """
        self.height = height
        return self
