from table_renderer import Table


def test_table_initialization_with_dimensions() -> None:
    """Test initializing a table with specific rows and columns."""
    table = Table(2, 3)
    assert len(table._cells) == 2
    assert len(table._cells[0]) == 3
    assert table._rows_count == 2
    assert table._cols_count == 3


def test_table_auto_growth_on_access() -> None:
    """Test that accessing out-of-bounds cells/rows/columns grows the table."""
    table = Table(1, 1)
    table.cell(5, 5).set_text("Growth")
    assert len(table._cells) == 6
    assert len(table._cells[0]) == 6

    table.get_row(10)
    assert len(table._row_objects) == 11

    table.get_column(8)
    assert len(table._col_objects) == 9


def test_table_merging_logic_correctly_marks_cells() -> None:
    """Test that merging logic correctly sets the is_merged flag on covered cells."""
    table = Table(4, 4)
    # Big merge: 3x3 starting at (0,0)
    table.cell(0, 0).span(rows=3, cols=3).set_text("Big")
    table._prepare_render()

    for r in range(3):
        for c in range(3):
            if r == 0 and c == 0:
                assert table.cell(r, c).is_merged is False
            else:
                assert table.cell(r, c).is_merged is True

    # Cell outside the merged area should remain unmerged
    assert table.cell(3, 3).is_merged is False


def test_table_cascading_inheritance_simulation() -> None:
    """Test style inheritance from Table -> Row/Col -> Cell."""
    table = Table(1, 1)
    table.set_font(size=20, color="green")
    table.get_row(0).set_font(color="red")
    table.cell(0, 0).set_background("blue")

    from table_renderer.renderer import render_to_html

    html = render_to_html(table)

    assert "font-size: 20px;" in html
    assert "color: red;" in html
    assert "background-color: blue;" in html
    assert 'class="row-0 col-0"' in html
