from typing import Self

from table_renderer.renderer import render_to_image, save_html

from .cell import Cell
from .column import Column
from .row import Row
from .style import StyledObject


class Table(StyledObject):
    """The main class representing a table to be rendered."""

    def __init__(self, rows: int = 0, cols: int = 0) -> None:
        """
        Initialize a table with initial dimensions.

        Args:
            rows: Initial number of rows.
            cols: Initial number of columns.
        """
        super().__init__()
        self._rows_count = rows
        self._cols_count = cols
        self._cells = [[Cell() for _ in range(cols)] for _ in range(rows)]
        self._row_objects = [Row(i) for i in range(rows)]
        self._col_objects = [Column(i) for i in range(cols)]
        self.width: int | str = "auto"
        self.font_files: list[str] = []

    def cell(self, row_index: int, col_index: int) -> Cell:
        """
        Get a cell at specific coordinates. Grows the table if needed.

        Args:
            row_index: Row index.
            col_index: Column index.

        Returns:
            The Cell object.
        """
        self._ensure_capacity(row_index, col_index)
        return self._cells[row_index][col_index]

    def get_row(self, row_index: int) -> Row:
        """
        Get a Row object. Grows the table if needed.

        Args:
            row_index: Row index.

        Returns:
            The Row object.
        """
        current_cols = len(self._cells[0]) if self._cells else 0
        self._ensure_capacity(row_index, max(0, current_cols - 1))
        return self._row_objects[row_index]

    def get_column(self, col_index: int) -> Column:
        """
        Get a Column object. Grows the table if needed.

        Args:
            col_index: Column index.

        Returns:
            The Column object.
        """
        current_rows = len(self._cells)
        self._ensure_capacity(max(0, current_rows - 1), col_index)
        return self._col_objects[col_index]

    def _ensure_capacity(self, target_row: int, target_col: int) -> None:
        """Efficiently grow the table to ensure it has at least target_row+1 rows and target_col+1 cols."""
        current_rows = len(self._cells)
        current_cols = len(self._cells[0]) if current_rows > 0 else 0

        target_rows = max(current_rows, target_row + 1)
        target_cols = max(current_cols, target_col + 1)

        # 1. Expand existing rows with new columns if needed
        cols_to_add = target_cols - current_cols
        if cols_to_add > 0:
            for row in self._cells:
                row.extend(Cell() for _ in range(cols_to_add))
            self._col_objects.extend(
                Column(i) for i in range(current_cols, target_cols)
            )

        # 2. Add new rows with the full target_cols capacity
        rows_to_add = target_rows - current_rows
        if rows_to_add > 0:
            self._cells.extend(
                [Cell() for _ in range(target_cols)] for _ in range(rows_to_add)
            )
            self._row_objects.extend(Row(i) for i in range(current_rows, target_rows))

    def set_width(self, width: int | str) -> Self:
        """
        Set the total width of the table.

        Args:
            width: Width in pixels or CSS value.

        Returns:
            The table itself for chaining.
        """
        self.width = width
        return self

    def add_font(self, font_path: str) -> Self:
        """
        Register a local font file.

        Args:
            font_path: Path to the .ttf or .otf file.

        Returns:
            The table itself for chaining.
        """
        self.font_files.append(font_path)
        return self

    def to_image(
        self,
        output_path: str,
        *,
        dpi: int = 144,
        padding: int = 10,
        background_color: str = "transparent",
    ) -> None:
        """
        Render the table to an image file.

        Args:
            output_path: Path to the output file (e.g., 'table.png', 'table.webp').
            dpi: Resolution of the output image.
            padding: Padding around the table in pixels.
            background_color: Background color of the image.
        """
        render_to_image(
            self,
            output_path,
            dpi=dpi,
            padding=padding,
            background_color=background_color,
        )

    def to_html(
        self, output_path: str, *, background_color: str = "transparent"
    ) -> None:
        """
        Export the table to an HTML file.

        Args:
            output_path: Path to the output HTML file.
            background_color: Background color of the HTML body.
        """
        save_html(self, output_path, background_color=background_color)

    def _prepare_render(self) -> None:
        """Handle merging logic and cascading styles before rendering."""
        # Reset is_merged flags
        for row_index in range(len(self._cells)):
            for col_index in range(len(self._cells[0])):
                self._cells[row_index][col_index].is_merged = False

        # Mark merged cells
        for row_index in range(len(self._cells)):
            for col_index in range(len(self._cells[0])):
                self._mark_merged_area(row_index, col_index)

    def _mark_merged_area(self, row_index: int, col_index: int) -> None:
        """Mark cells covered by a span as merged."""
        cell = self._cells[row_index][col_index]
        if cell.is_merged:
            return
        if cell.row_span > 1 or cell.col_span > 1:
            for d_row in range(cell.row_span):
                for d_col in range(cell.col_span):
                    if d_row == 0 and d_col == 0:
                        continue
                    if row_index + d_row < len(self._cells) and col_index + d_col < len(
                        self._cells[0]
                    ):
                        self._cells[row_index + d_row][
                            col_index + d_col
                        ].is_merged = True
