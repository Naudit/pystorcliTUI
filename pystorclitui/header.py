"""Provides a Textual application header widget."""

from __future__ import annotations

from datetime import datetime

from rich.text import Text

from textual.app import RenderResult
from textual.reactive import Reactive
from textual.widget import Widget


class HeaderLeftText(Widget):
    """Display a text on the left side of the header header."""

    DEFAULT_CSS = """
    HeaderLeftText {
        dock: left;
        padding: 0 1;
        content-align: left middle;
        background: $foreground-darken-1 5%;
        color: $text;
        text-opacity: 85%;
        width: 33%;
    }
    """

    text: Reactive[str] = Reactive("")

    def render(self) -> RenderResult:
        """Render the text

        Returns:
            The value to render.
        """
        return Text(self.text, no_wrap=True, overflow="ellipsis")


class HeaderRightText(Widget):
    """Display a text on the right side of the header header."""

    DEFAULT_CSS = """
    HeaderRightText {
        dock: right;
        padding: 0 1;
        content-align: right middle;
        background: $foreground-darken-1 5%;
        color: $text;
        text-opacity: 85%;
        width: 33%;
    }
    """

    text: Reactive[str] = Reactive("")

    def render(self) -> RenderResult:
        """Render the text

        Returns:
            The value to render.
        """
        return Text(self.text, no_wrap=True, overflow="ellipsis")


class HeaderCenterText(Widget):
    """Display a text on the center of the header header."""

    DEFAULT_CSS = """
    HeaderCenterText {
        content-align: center middle;
        background: $foreground-darken-1 5%;
        color: $text;
        text-opacity: 85%;
        width: 100%;
    }
    """

    text: Reactive[str] = Reactive("")
    """The main title text."""

    def render(self) -> RenderResult:
        """Render the text

        Returns:
            The value to render.
        """
        return Text(self.text, no_wrap=True, overflow="ellipsis")


class Header(Widget):
    """A header widget with icon and clock."""

    DEFAULT_CSS = """
    Header {
        dock: top;
        width: 100%;
        background: $foreground 5%;
        color: $text;
        height: 1;
    }
    Header.-tall {
        height: 3;
    }
    """

    DEFAULT_CLASSES = ""

    tall: Reactive[bool] = Reactive(False)
    left_title: Reactive[str] = Reactive("")
    center_title: Reactive[str] = Reactive("")
    right_title: Reactive[str] = Reactive("")

    """Set to `True` for a taller header or `False` for a single line header."""

    def __init__(
        self,
        show_clock: bool = False,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        """Initialise the header widget.

        Args:
            show_clock: ``True`` if the clock should be shown on the right of the header.
            name: The name of the header widget.
            id: The ID of the header widget in the DOM.
            classes: The CSS classes of the header widget.
        """
        super().__init__(name=name, id=id, classes=classes)
        self._show_clock = show_clock

    def compose(self):
        yield HeaderLeftText()
        yield HeaderCenterText()
        yield HeaderRightText()

    def watch_tall(self, tall: bool) -> None:
        self.set_class(tall, "-tall")

    def on_click(self):
        pass
        # self.toggle_class("-tall")

    def on_mount(self) -> None:
        def set_left_title(title: str) -> None:
            self.query_one(HeaderLeftText).text = title

        def set_center_title(title: str) -> None:
            self.query_one(HeaderCenterText).text = title

        def set_right_title(title: str) -> None:
            self.query_one(HeaderRightText).text = title

        self.watch(self, "left_title", set_left_title)
        self.watch(self, "center_title", set_center_title)
        self.watch(self, "right_title", set_right_title)
