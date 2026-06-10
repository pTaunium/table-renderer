import table_renderer


def test_version_string() -> None:
    """Test that the package has a version string."""
    assert hasattr(table_renderer, "__version__")
    assert isinstance(table_renderer.__version__, str)
    # The default fallback in __init__.py is "0.5.0"
    assert table_renderer.__version__ == "0.5.0"
