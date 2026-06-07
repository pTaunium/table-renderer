from pathlib import Path

import pytest

from table_renderer import Table


def test_html_generation_basic(tmp_path: Path) -> None:
    """Test generating basic HTML with content and line breaks."""
    table = Table(1, 1)
    table.cell(0, 0).set_text("Line 1\nLine 2")
    output_path = tmp_path / "test.html"
    table.to_html(str(output_path))

    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "Line 1<br>Line 2" in content


def test_html_font_registration() -> None:
    """Test that registered fonts appear in the generated HTML."""
    table = Table(1, 1)
    table.add_font("my_custom_font.ttf")

    from table_renderer.renderer import render_to_html

    html = render_to_html(table)
    assert "@font-face" in html
    assert "my_custom_font" in html


@pytest.mark.parametrize("ext", ["png", "jpg", "webp"])
def test_image_generation_formats(tmp_path: Path, ext: str) -> None:
    """Test image generation in various formats."""
    table = Table(2, 2)
    table.cell(0, 0).set_text("Format Test").set_background("yellow")
    output_path = tmp_path / f"test.{ext}"
    table.to_image(str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_image_dpi_scaling(tmp_path: Path) -> None:
    """Test that DPI scaling affects the output image validly."""
    table = Table(1, 1)
    table.cell(0, 0).set_text("DPI Test")

    path_72 = tmp_path / "72.png"
    path_300 = tmp_path / "300.png"

    table.to_image(str(path_72), dpi=72)
    table.to_image(str(path_300), dpi=300)

    assert path_72.exists()
    assert path_300.exists()
    # 300 DPI should generally result in a larger file than 72 DPI
    assert path_300.stat().st_size >= path_72.stat().st_size


def test_image_embedding_in_html() -> None:
    """Test that embedding an image generates correct HTML tags and paths."""
    table = Table(1, 1)
    # Using a dummy path for testing resolution logic
    img_path = "assets/example_table.png"
    table.cell(0, 0).set_image(img_path, width=100)

    from table_renderer.renderer import render_to_html

    html = render_to_html(table)

    assert "<img" in html
    assert "file://" in html
    assert "width: 100px;" in html
    assert "assets/example_table.png" in html.replace("\\", "/")


def test_remote_image_url_in_html() -> None:
    """Test that a remote image URL is used directly in the generated HTML."""
    table = Table(1, 1)
    url = "https://example.com/remote_image.png"
    table.cell(0, 0).set_image(url, height=50)

    from table_renderer.renderer import render_to_html

    html = render_to_html(table)

    assert "<img" in html
    assert 'src="https://example.com/remote_image.png"' in html
    assert "height: 50px;" in html
