# AGENTS.md

## OVERVIEW

`table-renderer` is a Python library that renders structured tables into high-quality images (PNG, JPG, WebP) or HTML. It uses Jinja2 templates for HTML generation, WeasyPrint for CSS-based PDF layout, and `pypdfium2` for converting PDFs to images.

## STRUCTURE

```
.
├── src/table_renderer/         # Core library logic
│   ├── __init__.py             # Public API entry point (re-exports models)
│   ├── py.typed                # PEP 561 marker for type checker support
│   ├── renderer.py             # High-level facade (save_image, save_html)
│   ├── html_generator.py       # Jinja2 template rendering (render_to_html)
│   ├── models/                 # Data models
│   │   ├── __init__.py         # Re-exports: Cell, Column, Row, Style, StyledObject, Table
│   │   ├── table.py            # Table (top-level container)
│   │   ├── row.py              # Row
│   │   ├── column.py           # Column
│   │   ├── cell.py             # Cell (content, images, merge spans)
│   │   └── style.py            # Style, StyledObject (CSS property bags)
│   ├── backends/               # Pluggable rendering backends
│   │   ├── __init__.py         # Re-exports: ImageRenderer, WeasyPrintRenderer
│   │   ├── base.py             # ImageRenderer Protocol
│   │   └── weasyprint_renderer.py  # Default backend (WeasyPrint + pypdfium2)
│   └── templates/
│       └── table.html.j2       # Jinja2 HTML template
├── tests/                      # Test suite (pytest)
│   ├── conftest.py             # Shared fixtures
│   ├── unit/                   # Unit tests (models, style, version)
│   └── integration/            # End-to-end rendering tests
├── .github/workflows/          # CI/CD
│   ├── ci.yml                  # Lint → Test (3.12–3.14) → Build
│   └── release.yml             # Tag-triggered publish to PyPI
├── assets/                     # Static assets (example images)
├── CHANGELOG.md                # Release history
├── LICENSE                     # MIT
├── README.md                   # User-facing documentation
├── README.zh-TW.md             # Traditional Chinese README
└── pyproject.toml              # Project configuration (uv, ruff, ty)
```

## WHERE TO LOOK

| Task               | Location                                             | Notes                                                   |
| ------------------ | ---------------------------------------------------- | ------------------------------------------------------- |
| Public API         | `src/table_renderer/__init__.py`                     | Re-exports models; version from metadata                |
| Data Models        | `src/table_renderer/models/`                         | Table, Row, Column, Cell, Style, StyledObject           |
| Rendering Facade   | `src/table_renderer/renderer.py`                     | `save_image`, `save_html`, deprecated `render_to_image` |
| HTML Generation    | `src/table_renderer/html_generator.py`               | Jinja2 context prep and `render_to_html`                |
| Backend Protocol   | `src/table_renderer/backends/base.py`                | `ImageRenderer` Protocol                                |
| WeasyPrint Backend | `src/table_renderer/backends/weasyprint_renderer.py` | Default image rendering backend                         |
| HTML Template      | `src/table_renderer/templates/table.html.j2`         | CSS/HTML layout for tables                              |
| Unit Tests         | `tests/unit/`                                        | Models, style, version                                  |
| Integration Tests  | `tests/integration/`                                 | End-to-end image rendering                              |
| CI/CD              | `.github/workflows/`                                 | `ci.yml` (lint/test/build), `release.yml` (publish)     |
| Changelog          | `CHANGELOG.md`                                       | Release notes per version                               |
| Build Config       | `pyproject.toml`                                     | Dependencies, ruff, ty, coverage config                 |

## CONVENTIONS

- **Documentation**: Use Google-style docstrings for all public methods.
- **API Design**:
  - Use keyword-only arguments for optional parameters (using the `*` separator).
  - Prefer absolute imports from the package root.
- **Naming**:
  - Variables/Functions/Methods: `snake_case`
  - Classes/Exceptions: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Private members: `_prefix_underscore`
  - Booleans: Use `is_`, `has_`, `can_`, `should_` prefixes.
- **Deprecation Policy**:
  - When renaming or deprecating public APIs, preserve the old signature as an alias.
  - Decorate the old function/method with `@typing_extensions.deprecated("Use `new_name` instead.")`.
  - Inside the old function, raise a runtime warning using `warnings.warn(..., DeprecationWarning, stacklevel=2)`.
- **Architecture**:
  - **KISS**: Prefer the simplest solution.
  - **SRP**: Keep data models (`models/`) separate from rendering logic (`renderer.py`, `html_generator.py`).
  - **Composition**: Favor combining objects over inheritance.
  - **Rule of Three**: Abstract only after three instances of duplication.
  - **Pluggable backends**: New rendering engines implement the `ImageRenderer` Protocol.

## COMMANDS

### Environment & Setup

- Install dependencies: `uv sync`
- Update lockfile: `uv lock`

### Quality Assurance

- Format: `uv run ruff format .`
- Lint: `uv run ruff check .`
- Type Check: `uv run ty check .`
- Run Tests: `uv run pytest tests/`
- Run Tests with Coverage: `uv run pytest --cov=src/ tests/`

### Build & Release

- Build package: `uv build`
- Publish to PyPI: `uv publish`

## NOTES

- **Rendering Dependencies**: Integration tests and rendering require system packages: `libpango-1.0-0`, `libpangoft2-1.0-0`, `libharfbuzz-subset0`.
- **CI/CD**: Pipeline triggers on push/PR to `main` (or `master`), running lint → tests across Python 3.12–3.14 → build. Releases are triggered by pushing a `v*.*.*` tag, which builds, publishes to PyPI, and creates a GitHub Release with extracted changelog notes.
