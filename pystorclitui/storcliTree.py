
import rich.repr

from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from pystorcli import StorCLI, Controllers, Controller, Enclosures, Enclosure, Drive, VirtualDrives, VirtualDrive
from rich.console import RenderableType
from rich.text import Text
from textual import events
from textual._types import MessageTarget
from textual.message import Message
from textual.reactive import Reactive
from textual.widgets import TreeControl, TreeClick, TreeNode, NodeID
from typing import Optional, Union, List, Dict


class SCEntryType(Enum):
    ControllerType = 1
    EnclosureType = 2
    DriveType = 3
    VDriveType = 4
    EnclosureLabel = 12
    VDriveLabel = 14


@dataclass
class StorcliEntry:
    controller: Controller
    enclosure: Union[None, Enclosure] = None
    drive: Union[None, Drive] = None
    vdrive: Union[None, VirtualDrive] = None
    type: SCEntryType = SCEntryType.ControllerType

    @property
    def can_be_expanded(self) -> bool:
        return self.type not in [SCEntryType.DriveType]


@rich.repr.auto
class StorcliClick(Message, bubble=True):
    def __init__(self, sender: MessageTarget, entry: StorcliEntry) -> None:
        self.entry = entry
        super().__init__(sender)


class StorcliTree(TreeControl[StorcliEntry]):
    def __init__(self, name: str = None) -> None:
        label = 'Controllers'
        data = StorcliEntry(None, 0)
        super().__init__(label, name=name, data=data)
        self.root.tree.guide_style = "bright_black"

    has_focus: Reactive[bool] = Reactive(False)

    def on_focus(self) -> None:
        self.has_focus = True

    def on_blur(self) -> None:
        self.has_focus = False

    async def watch_hover_node(self, hover_node: NodeID) -> None:
        for node in self.nodes.values():
            node.tree.guide_style = (
                "bold not dim bright_black" if node.id == hover_node else "bright_black"
            )
        self.refresh(layout=True)

    def render_node(self, node: TreeNode[StorcliEntry]) -> RenderableType:
        return self.render_tree_label(
            node,
            node.data.type,
            node.expanded,
            node.is_cursor,
            node.id == self.hover_node,
            self.has_focus,
        )

    def _drive_label_style(self, drive: Drive):
        state = drive.state

        if state == 'good':
            return 'bright_green'
        elif state == 'bad':
            return 'bold red'
        elif state == 'dhs' or state == 'ghs':
            return 'bright_cyan'
        elif state == 'online':
            return 'bright_cyan'
        elif state == 'offline':
            return 'dim red'

    @lru_cache(maxsize=1024 * 32)
    def render_tree_label(
        self,
        node: TreeNode[StorcliEntry],
        type: SCEntryType,
        expanded: bool,
        is_cursor: bool,
        is_hover: bool,
        has_focus: bool,
    ) -> RenderableType:
        meta = {
            "@click": f"click_label({node.id})",
            "tree_node": node.id,
            "cursor": node.is_cursor,
        }

        # Useful future symbols: ✇ ✨ ❌✗✘✓✔ ⛔⚠⚡⚪⚫ ✔✖
        # More symbols (arrows): ↶↷↺↻ -- https://www.w3schools.com/charsets/ref_utf_arrows.asp
        # Loafing symbols? ◜◝◞◟  ◔
        label = Text(node.label) if isinstance(node.label, str) else node.label
        if is_hover:
            label.stylize("underline")
        if type == SCEntryType.ControllerType:
            label.stylize("bold magenta")
            icon = "📂" if expanded else "📁"
        elif type == SCEntryType.EnclosureType:
            label.stylize("bold green")
            icon = "📂" if expanded else "📁"
        elif type == SCEntryType.EnclosureLabel:
            label.stylize("bold green")
            icon = "📂" if expanded else "📁"
        elif type == SCEntryType.VDriveLabel:
            label.stylize("bold green")
            icon = "📂" if expanded else "📁"
        elif type == SCEntryType.DriveType:
            label.stylize(self._drive_label_style(node.data.drive))
            icon = "🖴"
            label.highlight_regex(r"\..*$", "green")
        else:
            label.stylize("bright_cyan")
            icon = "🖴"
            label.highlight_regex(r"\..*$", "green")

        if is_cursor and has_focus:
            label.stylize("reverse")

        icon_label = Text(f"{icon} ", no_wrap=True,
                          overflow="ellipsis") + label
        icon_label.apply_meta(meta)
        return icon_label

    async def drop_caches(self) -> None:
        """Drop the caches of the tre and storcli."""
        # Drop the storcli cache
        StorCLI().clear_cache()

        # Drop the lru caches
        self.render_tree_label.cache_clear()

    async def reload(self) -> None:
        """Reload the tree."""

        # Drop current nodes
        self.nodes[NodeID(self.id)] = self.root
        self.root.children = []
        self.root._tree.children = []

        # Drop the caches
        await self.drop_caches()

        # Reload the entries
        await self.load_storcliEntries(self.root)

    async def on_mount(self, event: events.Mount) -> None:
        await self.load_storcliEntries(self.root)

    async def load_storcliEntries(self, node: TreeNode[StorcliEntry]):

        # First load
        if node == self.root:
            controllers = Controllers()
            for controller in controllers:
                await node.add(f'Controller{controller.id}', StorcliEntry(controller))
        else:
            # Load children

            ### Physical Controllers and media ###
            if node.data.type == SCEntryType.ControllerType:
                # Just add labels to group the enclosures and virtual drives
                await node.add(f'Enclosures', StorcliEntry(node.data.controller, type=SCEntryType.EnclosureLabel))
                await node.add(f'Virtual Drives', StorcliEntry(node.data.controller, type=SCEntryType.VDriveLabel))

            elif node.data.type == SCEntryType.EnclosureLabel:
                enclosures = node.data.controller.encls
                for enclosure in enclosures:
                    await node.add(f'Enclosure{enclosure.id}', StorcliEntry(node.data.controller, enclosure, type=SCEntryType.EnclosureType))

            elif node.data.type == SCEntryType.EnclosureType:
                drives = node.data.enclosure.drives
                for drive in drives:
                    await node.add(f'Drive{drive.id}', StorcliEntry(node.data.controller, node.data.enclosure, drive, type=SCEntryType.DriveType))

            # Virtual media
            elif node.data.type == SCEntryType.VDriveLabel:
                vdrives = node.data.controller.vds
                for vdrive in vdrives:
                    await node.add(f'Virtual Drive{vdrive.id}', StorcliEntry(node.data.controller, vdrive=vdrive, type=SCEntryType.VDriveType))

        node.loaded = True
        await node.expand()
        self.refresh(layout=True)

    async def handle_tree_click(self, message: TreeClick[StorcliEntry]) -> None:
        dir_entry = message.node.data

        # Expand if possible
        if dir_entry.can_be_expanded:
            if not message.node.loaded:
                await self.load_storcliEntries(message.node)
                await message.node.expand()
            else:
                await message.node.toggle()

        # Notify click
        await self.emit(StorcliClick(self, dir_entry))
