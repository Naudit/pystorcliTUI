# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Rafael Leira, Naudit HPCN S.L.
#
# See LICENSE for details.
#
################################################################

import json
import os
import pytest

from pystorcli import StorCLI
from .baseTest import TestStorcliMainClass


# discover tests
dataset_main_path = './tests/datasest/storcliSet/'

folders = [dataset_main_path +
           p for p in os.listdir(dataset_main_path)]


class TestStorcliMainClass(TestStorcliMainClass):

    @pytest.mark.parametrize("folder", folders)
    def test_init_invalid_exec(self, folder):
        from pystorcli.exc import StorCliError

        StorCLI.disable_singleton()

        with pytest.raises(StorCliError):
            storcli = StorCLI(binary='idontexist')
