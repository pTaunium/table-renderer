from table_renderer import Cell, Column, Row, StyledObject


def test_styled_object_setters_update_style() -> None:
    """Test that all setter methods in StyledObject correctly update the internal Style."""
    obj = StyledObject()
    obj.set_font(size=12, color="blue", family="Arial", weight="bold")
    obj.set_background("white")
    obj.set_align(horizontal="center", vertical="middle")
    obj.set_border(width=1, color="black", style="solid")

    assert obj.style.font_size == 12
    assert obj.style.font_color == "blue"
    assert obj.style.font_family == "Arial"
    assert obj.style.font_weight == "bold"
    assert obj.style.bg_color == "white"
    assert obj.style.text_align == "center"
    assert obj.style.vertical_align == "middle"
    assert obj.style.border_width == 1


def test_cell_initialization_and_setters() -> None:
    """Test Cell specific functionality."""
    cell = Cell("Init")
    assert cell.value == "Init"
    cell.set_text("New")
    assert cell.value == "New"
    cell.span(rows=2, cols=3)
    assert cell.row_span == 2
    assert cell.col_span == 3


def test_row_initialization() -> None:
    """Test Row initialization."""
    row = Row(index=5)
    assert row.index == 5


def test_column_initialization_and_width() -> None:
    """Test Column initialization and width setting."""
    col = Column(index=2)
    assert col.index == 2
    assert col.width == "auto"
    col.set_width(150)
    assert col.width == 150
    col.set_width("20%")
    assert col.width == "20%"
