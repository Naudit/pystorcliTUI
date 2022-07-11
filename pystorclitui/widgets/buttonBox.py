from rich.panel import Panel
from rich.console import RenderableType, StyleType

from textual.app import App
from textual.reactive import Reactive
from textual.widgets import Button


class ButtonBox(Button):

    def __init__(
        self,
        label: RenderableType,
        name: str | None = None,
        style: StyleType = "bold white",
        hover_style: StyleType = "bold white on dark_green",
        press_style: StyleType = "bold white on green",
    ):
        super().__init__(label=label, name=name, style=style)
        self.hover_style = hover_style
        self.press_style = press_style

    mouse_over = Reactive(False)
    mouse_press = Reactive(False)

    def render(self) -> Panel:
        if self.mouse_over:
            if self.mouse_press:
                style = self.press_style
            else:
                style = self.hover_style
        else:
            style = self.button_style

        return Panel(self.label, style=style)

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False
        self.mouse_press = False

    def on_mouse_down(self) -> None:
        self.mouse_press = True

    def on_mouse_up(self) -> None:
        self.mouse_press = False
