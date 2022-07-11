# -*- coding: utf-8 -*-

# Copyright (c) 2022, Rafael Leira & Naudit HPCN S.L. <rafael.leira@naudit.es>
# See LICENSE for details.

from textual._easing import EASING
from textual.app import App
from textual.reactive import Reactive
from textual.views import DockView, GridView
from textual.view import View
from textual.widgets import Button, Footer, TreeControl, ScrollView
from pystorcli import StorCLI, __version__ as pystorcli_version

from .storcliTree import StorcliTree, StorcliEntry, StorcliClick, SCEntryType
from . import header
from .version import __version__

from .views.drive import DriveView


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
            self.storcli = StorCLI()
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
