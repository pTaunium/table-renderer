# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **CSS Specificity**: Swapped the generation order of `.col-*` and `.row-*` CSS classes to ensure that `Row` styles correctly override `Column` styles when cascading, aligning with intuitive table formatting behavior.


## [0.3.0] - 2026-06-09

### Added
- **Configurable Background Color**: Added `background_color` parameter to HTML and image export methods to allow overriding the default transparent background.

### Performance
- **CSS Cascading**: Massively improved rendering speed and memory usage for large tables by shifting style merging from Python object allocation ($O(R \times C)$) to native CSS class cascading.
- **Render Loop Optimization**: Removed redundant bounds-checking loops during the hot path of rendering.
- **Memory-Efficient Auto-Crop**: Reduced memory usage during the visual auto-crop phase by ~66% by analyzing images in Grayscale (`L` mode) instead of `RGB/RGBA`.

### Fixed
- **Default Table Width**: Changed the default `Table` width from `"100%"` to `"auto"` to prevent tables from expanding unnecessarily to fill the safety canvas, resulting in much tighter and more accurate auto-crops.

## [0.2.0] - 2026-06-09

### Added
- **Dynamic Sizing**: Added dynamic width and height estimation for the rendering canvas to optimize performance for small tables and prevent clipping for extremely wide tables.
- **Continuous Tables**: Support for rendering extremely long tables by automatically stitching multiple PDF pages into a single continuous long image.

### Fixed
- **Transparency**: Resolved an issue where PDF backgrounds were rendered as solid white instead of transparent. PNG and WebP outputs now correctly preserve transparency.
- **JPG Export**: Fixed an `OSError` that occurred when saving RGBA images as JPG by automatically flattening them onto a white background.

### Changed
- **API (Breaking)**: Refactored public API methods (`set_font`, `set_align`, `set_border`, `set_image`, `span`, `to_image`) to enforce keyword-only arguments for optional parameters, reducing ambiguity and preventing positional argument errors.
- **Docs**: Aligned Docker `apt` dependencies with official WeasyPrint recommendations for Debian 11.

## [0.1.1] - 2026-06-07

### Added
- **Remote Images**: Added support for using remote URLs (`http://` or `https://`) directly in `cell.set_image()`.
- **Version String**: Added `__version__` string accessible directly from the `table_renderer` package.

### Security
- **CI Workflow**: Updated GitHub Actions permissions to explicitly require `contents: read` and `contents: write` (for releases).
- **Node.js 24 Support**: Upgraded CI actions (`checkout@v6`, `setup-uv@v8`) and enforced Node.js 24 to silence deprecation warnings and ensure future compatibility.

### Changed
- **CI**: Enabled full integration rendering tests in the CI pipeline.
- **CI**: Integrated Codecov for automated test coverage reporting.
- **Docs**: Changed the license badge color to the standard MIT blue.
- **CI**: Excluded `.gitignore` from GitHub Release artifacts.

## [0.1.0] - 2026-06-04

### Added
- Initial release of `table-renderer`.
- Clean Object-Oriented API (`Table`, `Row`, `Column`, `Cell`).
- Anchor-based cell merging (`span`).
- Cascading styling system (Table -> Row/Column -> Cell).
- High-quality HTML and Image (PNG, JPG, WebP) rendering powered by WeasyPrint and pypdfium2.
- Multi-language font stack support.
- Customizable DPI, padding, and image embedding in cells.
- Visual auto-crop feature.
- Comprehensive test suite with ~97% coverage.
- Fully automated CI/CD pipeline (Lint, Test, Build, Publish to PyPI and GitHub Releases).
