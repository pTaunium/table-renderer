from pathlib import Path

from table_renderer import Table


def test_long_table_rendering(tmp_path: Path) -> None:
    """Test that a very long table spanning multiple pages is rendered completely."""
    # Create a table with 100 rows to ensure it spans multiple A4 pages
    table = Table(100, 2)
    table.set_width(600)
    table.set_border(width=1, color="black", style="solid")

    for i in range(100):
        table.cell(i, 0).set_text(f"Row {i}")
        table.cell(i, 1).set_text(f"Value {i}")

    output_path = tmp_path / "long_table.png"
    # Render at low DPI for speed
    table.to_image(str(output_path), dpi=72)

    assert output_path.exists()

    # Verify image dimensions using Pillow
    from PIL import Image

    with Image.open(output_path) as img:
        # A single A4 page at 72 DPI is about 842px high.
        # 100 rows should be much taller than that.
        assert img.height > 1000
        # Check that the last row is likely there (visual check is hard, but size is a good proxy)
        print(f"Long table image height: {img.height}px")
