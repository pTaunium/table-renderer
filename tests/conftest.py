import pytest

from table_renderer import Table


@pytest.fixture
def sample_table() -> Table:
    """Provides a basic 3x3 table for testing."""
    table = Table(3, 3)
    table.cell(0, 0).set_text("Header")
    return table
