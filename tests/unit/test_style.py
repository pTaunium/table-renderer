from table_renderer import Style


def test_style_merge_basic_success() -> None:
    """Test that merging two styles correctly combines attributes."""
    s1 = Style(font_size=12, font_color="black")
    s2 = Style(font_color="red", background_color="yellow")
    merged = s1.merge(s2)

    assert merged.font_size == 12
    assert merged.font_color == "red"
    assert merged.background_color == "yellow"


def test_style_to_css_valid_conversion() -> None:
    """Test that style attributes are correctly converted to CSS strings."""
    style = Style(font_size=16, font_color="blue", font_family="Arial, sans-serif")
    css = style.to_css()
    assert "font-size: 16px;" in css
    assert "color: blue;" in css
    assert "font-family: 'Arial', 'sans-serif';" in css


def test_style_border_css_generation() -> None:
    """Test that specific border attributes generate correct CSS."""
    style = Style()
    style.border_bottom_width = 5
    style.border_bottom_color = "red"
    style.border_bottom_style = "dashed"

    css = style.to_css()
    assert "border-bottom-width: 5px;" in css
    assert "border-bottom-color: red;" in css
    assert "border-bottom-style: dashed;" in css
