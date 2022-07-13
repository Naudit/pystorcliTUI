from rich.panel import Panel, AlignMethod, Box, ROUNDED
from rich.console import RenderableType, StyleType

from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget


class MessageBox(Widget):

    title: Reactive[RenderableType] = Reactive("")
    content: Reactive[RenderableType] = Reactive("")

    def __init__(
        self,
        content: RenderableType = "I'm an empty message box",
        title: str | None = None,
        title_align: AlignMethod = "left",
        name: str | None = None,
        style: StyleType = "bold white",
        border_style: StyleType = "none",
        box: Box = ROUNDED,
    ):
        super().__init__(name=name)

        self.content = content
        self.title = title
        self.title_align = title_align
        self.style = style
        self.border_style = border_style
        self.box = box

    def render(self) -> Panel:
        return Panel(self.content, title=self.title, title_align=self.title_align, style=self.style, border_style=self.border_style, box=self.box)
