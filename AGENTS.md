# AGENTS.md

## Project Overview

`table-renderer` is a Python library for rendering structured tables into high-quality images (PNG, JPG, WebP) or HTML.

- **Core Engine**: WeasyPrint for CSS-based layout and `pypdfium2` for PDF-to-image conversion.
- **Architecture**: Separated data models (`models/`) from rendering logic (`renderer.py`).
- **Key Dependencies**: `weasyprint`, `pypdfium2`, `jinja2`, `pillow`.

## Setup Commands

- Install dependencies: `uv sync`
- Update lockfile: `uv lock`
- Install dev dependencies: Included in `uv sync --all-groups`

## Development Workflow

- Main code resides in `src/table_renderer/`.
- Entry point for public API is `src/table_renderer/__init__.py`.
- To test changes manually, run: `uv run python demo.py`.
- Package management is handled by `uv`.

## Testing Instructions

- Run all tests: `uv run pytest tests/`
- Run tests with coverage: `uv run pytest --cov=src/table_renderer tests/`
- Integration tests (rendering): `tests/integration/test_rendering.py` and `tests/integration/test_long_table.py`.
- Unit tests: `tests/unit/`.
- Note: Integration tests require system-level libraries (`libpango`, `libcairo`, etc.) and fonts.

## Code Style

- **Formatting & Linting**: We use `ruff`.
  - Check: `uv run ruff check .`
  - Format: `uv run ruff format .`
- **Type Checking**: We use `ty`.
  - Check: `uv run ty check .`
- **Conventions**:
  - Use Google-style docstrings for all public methods.
  - Enforce keyword-only arguments for optional parameters using the `*` separator.
  - Prefer absolute imports from the package root (e.g., `from table_renderer.renderer import ...`).

## Build and Deployment

- Build package: `uv build`
- Versioning: Managed in `pyproject.toml` and synchronized in `src/table_renderer/__init__.py`.
- CI/CD: Handled via GitHub Actions (`.github/workflows/`).
  - `ci.yml`: Runs linting, type checking, and tests on push/PR.
- `release.yml`: Builds and publishes to PyPI and GitHub Releases on tag push (`v*.*.*`).

## Pull Request Guidelines

- Ensure `uv run ruff format --check .`, `uv run ruff check .`, and `uv run ty check .` all pass.
- Ensure all tests pass: `uv run pytest tests/`.
- Follow conventional commit messages (e.g., `feat:`, `fix:`, `chore:`, `docs:`, `perf:`).
- Keep `CHANGELOG.md` updated in the `[Unreleased]` section.
