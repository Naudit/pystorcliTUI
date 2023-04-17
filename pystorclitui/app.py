# -*- coding: utf-8 -*-

# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

from textual._easing import EASING
from textual.app import App
from textual.reactive import Reactive
from textual.views import DockView, GridView
from textual.view import View
from textual.widgets import Button, Footer, TreeControl, ScrollView, Placeholder
from pystorcli import StorCLI, __version__ as pystorcli_version

from .storcliTree import StorcliTree, StorcliEntry, StorcliClick, SCEntryType
from . import header
from .version import __version__
from .storclicmdtui import StorcliCMDTUI, StorcliExec
from .views.drive import DriveView
from .widgets.messageBox import MessageBox


class PyStorCLITUI(App):
    """The pystorclitui application."""
    # Global variables
    storcli: StorCLI

    # Reactives
    show_tree = Reactive(True)

    # Widgets
    tree: StorcliTree

    # Views
    mainView: DockView
    treeView: ScrollView

    def __init__(self, storcli: StorCLI = None, *args, **kwargs):
        # Storcli instance
        if storcli is None:
            cmdRunner = StorcliCMDTUI()
            self.storcli = StorCLI(cmdrunner=cmdRunner)
        else:
            self.storcli = storcli

        # super init
        super().__init__(*args, **kwargs)

    def getEmptyMainView(self):
        """Return the basic view."""
        ret = Button(
            label="Please, select a Raid Card, Enclosure, Virtual Drive or Physical Drive to begin.",
            style="bold white on rgb(50,57,50)",
        )

        return ret

    async def on_load(self) -> None:
        """Bind keys here."""
        await self.bind("t", "toogle_tree", "Toggle device tree")
        await self.bind("r", "reload", "Reload StorCLI")
        await self.bind("q", "quit", "Quit")

        # Bind storcli events
        self.storcli._StorCLI__cmdrunner.set_parent(self)

    def action_toogle_tree(self) -> None:
        """Called when user hits 't' key."""
        self.show_tree = not self.show_tree

    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree changes."""
        # self.treeView.animate("layout_offset_x", 0 if show_tree else -40)
        self.treeView.visible = show_tree

    async def _set_main_view(self, view: View):
        # Clean up layout
        self.mainView.layout.docks.clear()
        self.mainView.widgets.clear()

        # Set the new layout/view
        await self.mainView.dock(view)

    async def action_reload(self) -> None:
        """Called when user hits 'r' key."""
        # Reload the tree
        await self.tree.reload()

        # Set default layout
        await self._set_main_view(self.getEmptyMainView())

        # Refresh
        self.refresh()

    async def on_mount(self) -> None:
        """Called when application mode is ready."""

        # Create the required Views
        self.mainView = DockView()

        # Header
        headr = header.Header()
        headr.center_title = f"PyStorCLI-TUI v{__version__}"
        headr.left_title = f"PyStorCLI v{pystorcli_version}"
        storcli_version = self.storcli.version
        headr.right_title = f"StorCLI v{storcli_version}"
        await self.view.dock(headr, edge="top")

        # Footer
        footer = Footer()
        await self.view.dock(footer, edge="bottom")

        # Device Tree
        self.tree = StorcliTree()
        await self.tree.root.expand()
        self.treeView = ScrollView(self.tree)

        # Message box
        self.messageBox = MessageBox(
            "Loading...", title="Storcli call in progress...")
        grid = await self.view.dock_grid(z=10)

        grid.add_column(fraction=1, name="left")
        grid.add_column(min_size=30, max_size=50, name="center")
        grid.add_column(fraction=1, name="right")
        grid.add_row(fraction=10, name="top")
        grid.add_row(fraction=1, name="middle", max_size=5, min_size=3)
        grid.add_row(fraction=10, name="bottom")

        grid.add_areas(
            area1="left,top",
            area2="center,middle",
            area3="left-start|right-end,bottom",
            area4="right,top-start|middle-end",
        )
        grid.place(area2=self.messageBox)

        self.messageBox.visible = False

        # Mount the Layout
        await self.view.dock(self.treeView, edge="left", size=32)
        await self.view.dock(self.mainView)
        await self.mainView.dock(self.getEmptyMainView())

    async def handle_storcli_click(self, message: StorcliClick) -> None:
        """Called in response to a tree click."""

        data: StorcliEntry = message.entry

        if data.type == SCEntryType.DriveType:
            # Show the drive view
            await self._set_main_view(DriveView(data.drive))

    async def handle_storcli_exec(self, message: StorcliExec) -> None:
        """Called in response to a storcli operation."""

        self.messageBox.content = 'Running: ' + ' '.join(message.cmdArgs)
        self.messageBox.visible = not message.finished
        # self.messageBox.refresh()
