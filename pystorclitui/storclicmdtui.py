# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Rafael Leira, Naudit HPCN S.L.
#
# See LICENSE for details.
#
################################################################


from pystorcli.cmdRunner import CMDRunner
from textual.widget import MessagePump
from textual.message import Message, MessageTarget
from typing import List
import subprocess
import logging
import rich


@rich.repr.auto
class StorcliExec(Message, bubble=True):
    cmdArgs: List[str]
    finished: bool

    def __init__(self, sender: MessageTarget, cmdArgs: List[str], finished=False) -> None:
        self.cmdArgs = cmdArgs
        self.finished = finished
        super().__init__(sender)


class StorcliCMDTUI(CMDRunner, MessagePump):
    """
    This class is wrapper of the CMDRunner class.
    It is used to notify upper TUI layers of wich command is being executed.
    """

    def __init__(self, upperRunner: CMDRunner = CMDRunner()):
        """Instantiates and initializes the storcli wrapper."""

        self.upperRunner = upperRunner
        super().__init__()

    def run(self, args, **kwargs) -> subprocess.CompletedProcess:
        """Runs a command and returns the output.
        """
        # Begin Execution
        if self.emit_no_wait(StorcliExec(self, args, False)):
            self.log('Emited StorcliExec')
        else:
            self.log('Issue with StorcliExec')

        # Run command
        ret = self.upperRunner.run(
            args=args, **kwargs)

        # End Execution
        self.emit_no_wait(StorcliExec(self, args, True))
        return ret

    def binaryCheck(self, binary):
        """Verify and return full binary path
        """

        return self.upperRunner.binaryCheck(binary)
