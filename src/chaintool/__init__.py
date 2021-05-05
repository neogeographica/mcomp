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

"""Initialize the package's modules."""


import atexit
import sys

import colorama

from . import command_impl_core
from . import completions
from . import locks
from . import sequence_impl_core
from . import shared
from . import shortcuts


__version__ = "0.3.0-dev"

if sys.version_info < (3, 7):
    sys.stderr.write("Python version 3.7 or later is required.\n")
    sys.exit(1)

colorama.init()
atexit.register(colorama.deinit)

shared.init()
last_version = shared.get_last_version()
command_impl_core.init(last_version, __version__)
sequence_impl_core.init(last_version, __version__)
locks.init(last_version, __version__)
shortcuts.init(last_version, __version__)
completions.init(last_version, __version__)
shared.set_last_version(__version__)
