from dataclasses import dataclass
from typing import Literal


@dataclass
class Style:
    """Represents the visual style of a table element."""

    font_size: int | None = None
    font_color: str | None = None
    font_family: str | None = None
    font_weight: Literal["normal", "bold"] | None = None
    bg_color: str | None = None
    text_align: Literal["left", "center", "right"] | None = None
    vertical_align: Literal["top", "middle", "bottom"] | None = None
    border_width: int | None = None
    border_color: str | None = None
    border_style: Literal["solid", "dashed", "dotted"] | None = None

    # Detailed borders
    border_top_width: int | None = None
    border_top_color: str | None = None
    border_top_style: Literal["solid", "dashed", "dotted"] | None = None

    border_bottom_width: int | None = None
    border_bottom_color: str | None = None
    border_bottom_style: Literal["solid", "dashed", "dotted"] | None = None

    border_left_width: int | None = None
    border_left_color: str | None = None
    border_left_style: Literal["solid", "dashed", "dotted"] | None = None

    border_right_width: int | None = None
    border_right_color: str | None = None
    border_right_style: Literal["solid", "dashed", "dotted"] | None = None

    def merge(self, other: "Style") -> "Style":
        """
        Merge another style into this one.

        Args:
            other: The style to merge. Attributes in 'other' take precedence.

        Returns:
            A new Style instance containing the merged attributes.
        """
        merged_style = Style(**self.__dict__)
        for k, v in other.__dict__.items():
            if v is not None:
                setattr(merged_style, k, v)
        return merged_style

    def to_css(self) -> str:
        """
        Convert style attributes to a CSS string.

        Returns:
            A string containing CSS property-value pairs.
        """
        css = []
        # Basic styles
        if self.font_size:
            css.append(f"font-size: {self.font_size}px;")
        if self.font_color:
            css.append(f"color: {self.font_color};")
        if self.font_family:
            # Handle font stacks: "Arial, Noto Sans" -> "'Arial', 'Noto Sans'"
            families = [
                f"'{f.strip()}'" if "'" not in f and '"' not in f else f.strip()
                for f in self.font_family.split(",")
            ]
            css.append(f"font-family: {', '.join(families)};")
        if self.font_weight:
            css.append(f"font-weight: {self.font_weight};")
        if self.bg_color:
            css.append(f"background-color: {self.bg_color};")
        if self.text_align:
            css.append(f"text-align: {self.text_align};")
        if self.vertical_align:
            css.append(f"vertical-align: {self.vertical_align};")

        # Borders
        css.extend(self._get_border_css())
        return " ".join(css)

    def _get_border_css(self) -> list[str]:
        """Internal helper to generate border CSS."""
        css = []
        if self.border_width:
            css.append(f"border-width: {self.border_width}px;")
        if self.border_color:
            css.append(f"border-color: {self.border_color};")
        if self.border_style:
            css.append(f"border-style: {self.border_style};")

        # Individual borders
        for side in ["top", "bottom", "left", "right"]:
            width = getattr(self, f"border_{side}_width")
            color = getattr(self, f"border_{side}_color")
            style = getattr(self, f"border_{side}_style")
            if width:
                css.append(f"border-{side}-width: {width}px;")
            if color:
                css.append(f"border-{side}-color: {color};")
            if style:
                css.append(f"border-{side}-style: {style};")
        return css
