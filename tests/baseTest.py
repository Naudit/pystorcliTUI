# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Rafael Leira, Naudit HPCN S.L.
#
# See LICENSE for details.
#
################################################################

import json
import os
from typing import List
from pystorcli import StorCLI
from .storclifile import StorcliCMDFile
from pystorclitui.storclicmdtui import StorcliCMDTUI


class TestStorcliMainClass():

    def get_cmdRunner(self, folder: str, options: List[str] = []):
        return StorcliCMDTUI(StorcliCMDFile(folder, options))

    def setupEnv(self, folder: str):
        # get cmdRunner
        cmdRunner = self.get_cmdRunner(folder)

        StorCLI.enable_singleton()

        return StorCLI(cmdrunner=cmdRunner)
