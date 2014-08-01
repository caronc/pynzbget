# -*- encoding: utf-8 -*-
#
# A Test Suite (for nose) for the ScriptBase Class
#
# Copyright (C) 2014 Chris Caron <lead2gold@gmail.com>
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
#
import os
import sys
from os.path import dirname
from os.path import join
sys.path.insert(0, join(dirname(dirname(__file__)), 'nzbget'))

from ScriptBase import ScriptBase
from ScriptBase import SYS_ENVIRO_ID
from ScriptBase import SHR_ENVIRO_ID
from ScriptBase import NZBGET_MSG_PREFIX

from TestBase import TestBase
from TestBase import TEMP_DIRECTORY

import StringIO

class TestScriptBase(TestBase):
    def setUp(self):
        # common
        super(TestScriptBase, self).setUp()

        # Create some environment variables
        os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY

    def tearDown(self):
        del os.environ['%sTEMPDIR' % SYS_ENVIRO_ID]

        # common
        super(TestScriptBase, self).tearDown()

    def test_set_and_get(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=True)

        KEY = 'MY_VAR'
        VALUE = 'MY_VALUE'

        # Value doe snot exist yet
        assert script.get(KEY) == None
        assert script.get(KEY, 'Default') == 'Default'
        assert script.set(KEY, VALUE) == True
        assert script.get(KEY, 'Default') == VALUE

    def test_pushes(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=True)

        KEY = 'MY_VAR'
        VALUE = 'MY_VALUE'

        # Value doe snot exist yet
        assert script.get(KEY) == None

        # Keep a handle on the real standard output
        stdout = sys.stdout
        sys.stdout = StringIO.StringIO()
        script.push(KEY, VALUE)

        # extract data
        sys.stdout.seek(0)
        output = sys.stdout.read().strip()

        # return stdout back to how it was
        sys.stdout = stdout
        assert output == '%s%s%s=%s' % (
            NZBGET_MSG_PREFIX,
            SHR_ENVIRO_ID,
            KEY,
            VALUE,
        )
        assert script.get(KEY) == VALUE
