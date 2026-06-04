from .base import StyledObject


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
