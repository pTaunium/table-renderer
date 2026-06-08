# Table Renderer 📊

<!-- README-I18N:START -->

**English** | [繁體中文](README.zh-TW.md)

<!-- README-I18N:END -->

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14-blue)](pyproject.toml)
[![CI](https://github.com/pTaunium/table-renderer/actions/workflows/ci.yml/badge.svg)](https://github.com/pTaunium/table-renderer/actions)
[![codecov](https://codecov.io/gh/pTaunium/table-renderer/graph/badge.svg)](https://codecov.io/gh/pTaunium/table-renderer)

`table-renderer` is a powerful and lightweight Python library designed to convert structured tables into high-quality images (PNG, JPG, WebP) or HTML. By combining the layout power of CSS with an intuitive Python API, it's perfect for automated reporting, Kubernetes CronJobs, or any data visualization task.

## ✨ Features

- **Broad Compatibility**: Fully supports **Python 3.12, 3.13, and 3.14**.
- **Business Friendly**: Uses `pypdfium2` (Apache-2.0) and `WeasyPrint` for a 100% MIT-compatible dependency chain.
- **High-Quality Rendering**: Powered by WeasyPrint (CSS engine), supporting complex text wrapping, alignment, and cell merging.
- **Auto-Crop**: Automatically crops images to the actual table area using visual detection, eliminating unnecessary white space.
- **Continuous Long Tables**: Automatically stitches multiple PDF pages into a single continuous long image, preventing content from being cut off.
- **Object-Oriented API**: Clean `Table` -> `Row/Column` -> `Cell` hierarchy with fluent interface support.
- **Cascading Styles**: Manage visual styles effortlessly with "Global Defaults + Local Overrides."
- **Multi-language Font Support**: Support for font stacks (e.g., different fonts for English and Chinese).
- **Customizable Resolution**: Adjustable DPI for high-resolution output (e.g., 300 DPI for print).
- **Lightweight Deployment**: No heavy browser dependencies (like Chromium), making it ideal for Docker/K8s.

---

## 🖼 Visual Example

Here is an example table generated using the code in the [Quick Start](#-quick-start) section:

![Example Table](assets/example_table.png)

---

## 🚀 Quick Start

### Installation

If you are developing within this project, use `uv`:

```bash
uv sync
```

To install it in another project:

```bash
pip install .
```

### Basic Usage

```python
from table_renderer import Table

# 1. Initialize a 3x3 table
table = Table(3, 3)
table.set_width(600)
table.set_border(width=1, color="black", style="solid")

# 2. Set header style (Row 0)
header = table.get_row(0)
header.set_background("#333").set_font(color="white", weight="bold", size=16)
header.set_align(horizontal="center")

table.cell(0, 0).set_text("Product")
table.cell(0, 1).set_text("Category")
table.cell(0, 2).set_text("Price")

# 3. Add content and demonstrate merging
table.cell(1, 0).set_text("MacBook Pro").span(rows=1, cols=2)
table.cell(1, 2).set_text("$2,000")

table.cell(2, 0).set_text("Magic Mouse")
table.cell(2, 1).set_text("Peripherals")
table.cell(2, 2).set_text("$79")

# 4. Global column styling (align prices to the right)
table.get_column(2).set_align(horizontal="right").set_width(100)

# 5. Export to image with custom DPI and padding
table.to_image("report.png", dpi=300, padding=20)
```

---

## 🛠 Advanced Features

### 1. Cell Merging

Use the anchor-based design to merge cells by specifying the starting cell and the span.

```python
# Merge first row, first two columns (1 row, 2 columns)
table.cell(0, 0).span(rows=1, cols=2).set_text("Merged Header")
```

### 2. Font Management

Load local font files and define font stacks for character-level fallback.

```python
# Load local font files (.ttf / .otf)
table.add_font("./fonts/Roboto-Regular.ttf")
table.add_font("./fonts/NotoSansTC-Medium.otf")

# Define a font stack: English prefers Roboto, Chinese falls back to Noto Sans
table.set_font(family="Roboto-Regular, NotoSansTC-Medium")
```

### 3. Embedding Images in Cells

You can embed both local images and remote URLs into any cell.

```python
# Set a local image
table.cell(1, 0).set_image("path/to/logo.png", width=50)

# Set a remote image URL
table.cell(1, 1).set_image("https://example.com/image.jpg", width=100)
```

### 4. Layout & Sizing

Mix fixed widths, percentages, and auto-sizing.

```python
table.set_width(800)                  # Total table width
table.get_column(0).set_width(200)    # Fixed 200px
table.get_column(1).set_width("auto") # Distribute remaining space
```

**Handling Extremely Wide Tables:**
The library dynamically estimates canvas width to prevent clipping. However, if your table contains unbreakable strings (like long URLs) and relies purely on auto-layout, you can manually override the canvas width. The auto-crop feature will automatically trim any excess white space.

```python
# Force a massive canvas width; auto-crop will cleanly trim the excess
table.set_width(15000)
table.to_image("wide_table.png")
```

### 5. DPI, Formats & Padding

Fine-tune your output image quality and margins.

```python
# High-res JPG with custom 20px padding
table.to_image("output.jpg", dpi=300, padding=20)

# Lightweight WebP with tight margins
table.to_image("output.webp", dpi=72, padding=0)
```

---

## 🐳 Docker / Kubernetes Deployment

Since `weasyprint` relies on system-level C libraries, your Dockerfile should include these dependencies:

```dockerfile
FROM python:3.12-slim

# Install system dependencies for WeasyPrint rendering and fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install .

CMD ["python", "main.py"]
```

---

## 🧪 Development

### Running Tests

We use `pytest` for testing. Ensure you have installed the development dependencies.

```bash
uv run pytest --cov=src/table_renderer tests/
```

### Linting & Formatting

We use `ruff` to maintain code quality.

```bash
uv run ruff check .
uv run ruff format .
```

---

## 🤝 Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.
