from typing import Literal, Self

from .style import Style


class StyledObject:
    """Base class for objects that can be styled."""

    def __init__(self) -> None:
        """Initialize with a default Style."""
        self.style = Style()

    def set_font(
        self,
        size: int | None = None,
        color: str | None = None,
        family: str | None = None,
        weight: Literal["normal", "bold"] | None = None,
    ) -> Self:
        """
        Set font related styles.

        Args:
            size: Font size in pixels.
            color: Text color (e.g., 'red', '#ff0000').
            family: Font family or font stack.
            weight: 'normal' or 'bold'.

        Returns:
            The object itself for chaining.
        """
        self.style.font_size = size or self.style.font_size
        self.style.font_color = color or self.style.font_color
        self.style.font_family = family or self.style.font_family
        self.style.font_weight = weight or self.style.font_weight
        return self

    def set_background(self, color: str) -> Self:
        """
        Set the background color.

        Args:
            color: Background color.

        Returns:
            The object itself for chaining.
        """
        self.style.bg_color = color
        return self

    def set_align(
        self,
        horizontal: Literal["left", "center", "right"] | None = None,
        vertical: Literal["top", "middle", "bottom"] | None = None,
    ) -> Self:
        """
        Set text alignment.

        Args:
            horizontal: Horizontal alignment.
            vertical: Vertical alignment.

        Returns:
            The object itself for chaining.
        """
        self.style.text_align = horizontal or self.style.text_align
        self.style.vertical_align = vertical or self.style.vertical_align
        return self

    def set_border(
        self,
        width: int | None = None,
        color: str | None = None,
        style: Literal["solid", "dashed", "dotted"] | None = None,
    ) -> Self:
        """
        Set border styles.

        Args:
            width: Border width in pixels.
            color: Border color.
            style: Border style.

        Returns:
            The object itself for chaining.
        """
        self.style.border_width = width or self.style.border_width
        self.style.border_color = color or self.style.border_color
        self.style.border_style = style or self.style.border_style
        return self
