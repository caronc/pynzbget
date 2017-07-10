# -*- encoding: utf-8 -*-
#
# A base testing class/library to help set some common testing vars
#
# Copyright (C) 2014-2017 Chris Caron <lead2gold@gmail.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

import os
import sys
from getpass import getuser
from tempfile import gettempdir
from os.path import join
from os.path import dirname
sys.path.insert(0, join(dirname(dirname(__file__)), 'nzbget'))

from os import makedirs
from shutil import rmtree

from nzbget.ScriptBase import SYS_OPTS_RE
from nzbget.ScriptBase import CFG_OPTS_RE
from nzbget.ScriptBase import SHR_OPTS_RE

TEMP_DIRECTORY = join(
    gettempdir(),
    'nzbget-test-%s' % getuser(),
)


class TestBase(object):
    def setUp(self):
        """This method is run once before _each_ test method is executed"""
        try:
            rmtree(TEMP_DIRECTORY)
        except:
            pass
        makedirs(TEMP_DIRECTORY, 0700)

    def tearDown(self):
        """This method is run once after _each_ test method is executed"""
        # Clean out System Environment
        for k in os.environ.keys():
            if SYS_OPTS_RE.match(k):
                del os.environ[k]
                continue
            if CFG_OPTS_RE.match(k):
                del os.environ[k]
                continue
            if SHR_OPTS_RE.match(k):
                del os.environ[k]
                continue

    def cleanup(self):
        """Remove the database"""
        try:
            rmtree(TEMP_DIRECTORY)
        except:
            pass
