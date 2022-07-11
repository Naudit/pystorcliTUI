from datetime import datetime
from logging import getLogger

from rich.console import Console, ConsoleOptions, RenderableType
from rich.panel import Panel
from rich.repr import rich_repr, Result
from rich.style import StyleType
from rich.table import Table
from rich.text import TextType

from textual import events
from textual.widget import Widget
from textual.reactive import watch, Reactive

log = getLogger("rich")


class Header(Widget):
    def __init__(
        self,
        *,
        tall: bool = True,
        style: StyleType = "white on dark_green",
        clock: bool = True,
    ) -> None:
        super().__init__()
        self.tall = tall
        self.style = style

    tall: Reactive[bool] = Reactive(True, layout=True)
    style: Reactive[StyleType] = Reactive("white on blue")
    left_title: Reactive[str] = Reactive("")
    center_title: Reactive[str] = Reactive("")
    right_title: Reactive[str] = Reactive("")

    @property
    def full_title(self) -> str:
        return f"{self.title} - {self.sub_title}" if self.sub_title else self.title

    def __rich_repr__(self) -> Result:
        yield self.title

    async def watch_tall(self, tall: bool) -> None:
        self.layout_size = 3 if tall else 1

    def get_clock(self) -> str:
        return datetime.now().time().strftime("%X")

    def render(self) -> RenderableType:
        header_table = Table.grid(padding=(0, 1), expand=True)
        header_table.style = self.style
        header_table.add_column(justify="left", ratio=0.5)
        header_table.add_column("title", justify="center", ratio=1)
        header_table.add_column("right_title", justify="right", ratio=0.5)
        header_table.add_row(
            self.left_title, self.center_title, self.right_title
        )
        header: RenderableType
        header = Panel(
            header_table, style=self.style) if self.tall else header_table
        return header

    async def on_click(self, event: events.Click) -> None:
        self.tall = not self.tall
