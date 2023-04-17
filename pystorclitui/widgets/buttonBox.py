from rich.panel import Panel
from rich.console import RenderableType, StyleType

from textual.app import App
from textual.reactive import Reactive
from textual.widgets import Button
from textual.events import Click


class ButtonBox(Button):

    def __init__(
        self,
        label: RenderableType,
        name: str | None = None,
        style: StyleType = "bold white",
        hover_style: StyleType = "bold white on dark_green",
        press_style: StyleType = "bold white on green",
        disabled_style: StyleType = "bold grey50",
        enabled: bool = True,
    ):
        super().__init__(label=label, name=name, style=style)
        self.hover_style = hover_style
        self.press_style = press_style
        self.disabled_style = disabled_style
        self.enabled = enabled

    mouse_over = Reactive(False)
    mouse_press = Reactive(False)

    def render(self) -> Panel:
        border_style = None
        if self.enabled:
            if self.mouse_over:
                if self.mouse_press:
                    style = self.press_style
                else:
                    style = self.hover_style
            else:
                style = self.button_style
        else:
            style = self.disabled_style
            border_style = "gray70"

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

    def disable(self) -> None:
        self.enabled = False

    def enable(self) -> None:
        self.enabled = True

    async def on_click(self, event: Click) -> None:
        if self.enabled:
            return await super().on_click(event)
