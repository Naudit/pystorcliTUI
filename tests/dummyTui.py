#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Rafael Leira, Naudit HPCN S.L.
#
# See LICENSE for details.
#
################################################################

"""This is a dummy TUI class for testing purposes. It will use the storclifile module to simulate a real server with storcli and a raid card installed."""

# Run me as: python -m tests.dummyTui

import os
import sys
from pystorclitui import PyStorCLITUI
from .baseTest import TestStorcliMainClass


class Main(TestStorcliMainClass):
    def main(self):
        storcli = self.setupEnv(os.path.abspath(os.path.join(
            os.path.dirname(__file__), "dataset/dummyTui")))

        PyStorCLITUI(storcli=storcli).run()


if __name__ == "__main__":
    Main().main()
