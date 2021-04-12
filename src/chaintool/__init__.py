# -*- coding: utf-8 -*-
#
# Copyright 2021 Joel Baxter
#
# This file is part of chaintool.
#
# chaintool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# chaintool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with chaintool.  If not, see <https://www.gnu.org/licenses/>.


import atexit
import os

import colorama

from . import completions
from .constants import DATA_DIR


__version__ = "0.1.0"

FIRST_RUN_MARKER = os.path.join(DATA_DIR, "firstrun-" + __version__)
if not os.path.exists(FIRST_RUN_MARKER):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(FIRST_RUN_MARKER, 'w'):
        pass
    completions.init()

colorama.init()
atexit.register(colorama.deinit)
