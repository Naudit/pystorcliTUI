# -*- coding: utf-8 -*-

# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

from ..widgets.buttonBox import ButtonBox
from rich.json import JSON
from rich.panel import Panel
from rich.style import Style
from textual_inputs import TextInput
from textual.views import DockView, GridView
from textual.widgets import Button, ButtonPressed, ScrollView
from typing import Union
import json
import pystorcli


class DriveView(DockView):

    drive:  pystorcli.Drive
    upper_grid: GridView
    options_grid: GridView

    def __init__(self, drive: pystorcli.Drive):
        self.drive = drive
        super().__init__()
        self.upper_grid = GridView()
        self.options_grid = GridView()

    async def on_mount(self) -> None:  # define input fields
        # Common properties
        button_style = "bold white"
        label_style = "bold white on rgb(50,57,50)"

        # Upper grid
        self.upper_grid.grid.set_align("center", "center")
        self.upper_grid.grid.set_gap(1, 1)
        # Create rows / columns / areas
        self.upper_grid.grid.add_column("column", fraction=1, min_size=10)
        self.upper_grid.grid.add_row("row", fraction=1, min_size=10)
        self.options_grid.grid.set_repeat(True, True)

        # Place out widgets in to top the layout
        outjson = JSON(json.dumps(self.drive._run(["show", "all"])))
        properties = ScrollView(outjson)
        self.upper_grid.grid.place(properties)

        # Set up the options grid
        self.options_grid.grid.set_align("center", "center")
        self.options_grid.grid.set_gap(0, 0)
        # Create rows / columns / areas
        self.options_grid.grid.add_column(
            "column", fraction=1, max_size=20)
        self.options_grid.grid.add_row(
            "row", fraction=1, max_size=3)
        self.options_grid.grid.set_repeat(True, True)
        # Place out widgets in to the layout
        drive_spin_toggle_button = ButtonBox(
            label="Spin Down", name="toggle_spin", style=button_style)
        drive_reset_errors_button = ButtonBox(
            label="Reset Errors", name="reset_errors", style=button_style)
        drive_set_state_missing_button = ButtonBox(
            label="Set Missing", name="set_missing", style=button_style)
        drive_set_state_online_button = ButtonBox(
            label="Set Online", name="set_online", style=button_style)
        drive_blink_button = ButtonBox(
            label="Blink ✨", name="toggle_blink", style=button_style)
        self.options_grid.grid.place(drive_spin_toggle_button)
        self.options_grid.grid.place(drive_reset_errors_button)
        self.options_grid.grid.place(drive_set_state_missing_button)
        self.options_grid.grid.place(drive_set_state_online_button)
        self.options_grid.grid.place(drive_blink_button)

        # Dock the grids
        await self.dock(self.options_grid, edge="bottom", size=7)
        await self.dock(self.upper_grid, edge="top")
