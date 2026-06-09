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
        while row_index >= len(self._cells):
            self._add_row()
        while col_index >= len(self._cells[0]):
            self._add_col()
        return self._cells[row_index][col_index]

    def get_row(self, row_index: int) -> Row:
        """
        Get a Row object. Grows the table if needed.

        Args:
            row_index: Row index.

        Returns:
            The Row object.
        """
        while row_index >= len(self._row_objects):
            self._add_row()
        return self._row_objects[row_index]

    def get_column(self, col_index: int) -> Column:
        """
        Get a Column object. Grows the table if needed.

        Args:
            col_index: Column index.

        Returns:
            The Column object.
        """
        while col_index >= len(self._col_objects):
            self._add_col()
        return self._col_objects[col_index]

    def _add_row(self) -> None:
        """Internal helper to add a row."""
        new_row_idx = len(self._cells)
        cols_count = len(self._cells[0]) if self._cells else self._cols_count
        self._cells.append([Cell() for _ in range(cols_count)])
        self._row_objects.append(Row(new_row_idx))

    def _add_col(self) -> None:
        """Internal helper to add a column."""
        for row in self._cells:
            row.append(Cell())
        self._col_objects.append(Column(len(self._col_objects)))

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
