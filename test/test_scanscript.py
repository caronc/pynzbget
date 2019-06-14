# -*- encoding: utf-8 -*-
#
# A Test Suite (for nose) for the ScanScript Class
#
# Copyright (C) 2014-2019 Chris Caron <lead2gold@gmail.com>
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
from os.path import join

from TestBase import TestBase
from TestBase import TEMP_DIRECTORY

from nzbget.ScriptBase import CFG_ENVIRO_ID
from nzbget.ScriptBase import SYS_ENVIRO_ID
from nzbget.ScriptBase import NZBGET_MSG_PREFIX

from nzbget.ScanScript import ScanScript
from nzbget.ScanScript import SCAN_ENVIRO_ID
from nzbget.ScanScript import PRIORITY


from nzbget.Logger import VERY_VERBOSE_DEBUG

try:
    # Python v2.7
    from StringIO import StringIO
except ImportError:
    # Python v3.x
    from io import StringIO

# Some constants to work with
DIRECTORY = TEMP_DIRECTORY
NZBNAME = 'The.Perfect.Name'
FILENAME = join(TEMP_DIRECTORY, 'nzbget/the/The.Perfect.Name.nzb')
CATEGORY = 'movie'
_PRIORITY = PRIORITY.NORMAL
TOP = False
PAUSED = False


class TestScanScript(TestBase):
    def setup_method(self):
        """This method is run once before _each_ test method is executed"""
        super(TestScanScript, self).setup_method()

        # Create some environment variables
        os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = DIRECTORY
        os.environ['%sNZBNAME' % SCAN_ENVIRO_ID] = NZBNAME
        os.environ['%sFILENAME' % SCAN_ENVIRO_ID] = FILENAME
        os.environ['%sCATEGORY' % SCAN_ENVIRO_ID] = CATEGORY
        os.environ['%sPRIORITY' % SCAN_ENVIRO_ID] = str(_PRIORITY)
        os.environ['%sTOP' % SCAN_ENVIRO_ID] = str(int(TOP))
        os.environ['%sPAUSED' % SCAN_ENVIRO_ID] = str(int(PAUSED))

    def teardown_method(self):
        """This method is run once after _each_ test method is executed"""
        # Eliminate any variables defined
        del os.environ['%sTEMPDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]
        del os.environ['%sNZBNAME' % SCAN_ENVIRO_ID]
        del os.environ['%sFILENAME' % SCAN_ENVIRO_ID]
        del os.environ['%sCATEGORY' % SCAN_ENVIRO_ID]
        del os.environ['%sPRIORITY' % SCAN_ENVIRO_ID]
        del os.environ['%sTOP' % SCAN_ENVIRO_ID]
        del os.environ['%sPAUSED' % SCAN_ENVIRO_ID]

        # common
        super(TestScanScript, self).teardown_method()

    def test_environment_varable_init(self):
        """
        Testing NZBGet Script initialization using environment variables
        """
        # a NZB Logger set to False uses stderr
        script = ScanScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.directory == DIRECTORY
        assert script.nzbname == NZBNAME
        assert script.filename == FILENAME
        assert script.category == CATEGORY
        assert script.priority == _PRIORITY
        assert script.top == TOP
        assert script.paused == PAUSED

        assert script.system['TEMPDIR'] == TEMP_DIRECTORY
        assert script.system['DIRECTORY'] == DIRECTORY
        assert script.system['NZBNAME'] == NZBNAME
        assert script.system['FILENAME'] == FILENAME
        assert script.system['CATEGORY'] == CATEGORY
        assert script.system['PRIORITY'] == _PRIORITY
        assert script.system['TOP'] == TOP
        assert script.system['PAUSED'] == PAUSED

        assert script.get('TEMPDIR') == TEMP_DIRECTORY
        assert script.get('DIRECTORY') == DIRECTORY
        assert script.get('NZBNAME') == NZBNAME
        assert script.get('FILENAME') == FILENAME
        assert script.get('CATEGORY') == CATEGORY
        assert script.get('PRIORITY') == _PRIORITY
        assert script.get('TOP') == TOP
        assert script.get('PAUSED') == PAUSED

        assert len(script.config) == 1
        assert script.config.get('DEBUG') == VERY_VERBOSE_DEBUG

        assert os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] == TEMP_DIRECTORY
        assert os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] == DIRECTORY
        assert os.environ['%sNZBNAME' % SCAN_ENVIRO_ID] == NZBNAME
        assert os.environ['%sFILENAME' % SCAN_ENVIRO_ID] == FILENAME
        assert os.environ['%sCATEGORY' % SCAN_ENVIRO_ID] == CATEGORY
        assert os.environ['%sPRIORITY' % SCAN_ENVIRO_ID] == str(_PRIORITY)
        assert os.environ['%sTOP' % SCAN_ENVIRO_ID] == str(int(TOP))
        assert os.environ['%sPAUSED' % SCAN_ENVIRO_ID] == str(int(PAUSED))

    def test_environment_override(self):
        """
        Testing NZBGet Script initialization using forced variables that
        should take priority over global ones
        """
        directory = join(DIRECTORY, 'a', 'deeper', 'path')
        nzbname = '%s.with.more.detail' % NZBNAME
        filename = '%s.with.more.detail' % FILENAME
        category = '%s.with.more.detail' % CATEGORY
        priority = PRIORITY.FORCE
        top = not TOP
        paused = not PAUSED

        script = ScanScript(
            logger=False,
            debug=VERY_VERBOSE_DEBUG,

            directory=directory,
            nzbname=nzbname,
            filename=filename,
            category=category,
            priority=priority,
            top=top,
            paused=paused,
        )

        assert script.directory == directory
        assert script.nzbname == nzbname
        assert script.filename == filename
        assert script.category == category
        assert script.priority == priority
        assert script.top == top
        assert script.paused == paused

        assert script.system['TEMPDIR'] == TEMP_DIRECTORY
        assert script.system['DIRECTORY'] == directory
        assert script.system['NZBNAME'] == nzbname
        assert script.system['FILENAME'] == filename
        assert script.system['CATEGORY'] == category
        assert script.system['PRIORITY'] == priority
        assert script.system['TOP'] == top
        assert script.system['PAUSED'] == paused

        assert len(script.config) == 1
        assert script.config.get('DEBUG') == VERY_VERBOSE_DEBUG

        assert os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] == TEMP_DIRECTORY
        assert os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] == directory
        assert os.environ['%sNZBNAME' % SCAN_ENVIRO_ID] == nzbname
        assert os.environ['%sFILENAME' % SCAN_ENVIRO_ID] == filename
        assert os.environ['%sCATEGORY' % SCAN_ENVIRO_ID] == category
        assert os.environ['%sPRIORITY' % SCAN_ENVIRO_ID] == str(priority)
        assert os.environ['%sTOP' % SCAN_ENVIRO_ID] == str(int(top))
        assert os.environ['%sPAUSED' % SCAN_ENVIRO_ID] == str(int(paused))

    def test_set_and_get(self):
        # a NZB Logger set to False uses stderr
        script = ScanScript(logger=False, debug=VERY_VERBOSE_DEBUG)

        KEY = 'MY_VAR'
        VALUE = 'MY_VALUE'

        # Value doe snot exist yet
        assert script.get(KEY) is None
        assert script.get(KEY, 'Default') == 'Default'
        assert script.set(KEY, VALUE) is True
        assert script.get(KEY, 'Default') == VALUE

    def test_config_varable_init(self):
        valid_entries = {
            'MY_CONFIG_ENTRY': 'Option A',
            'ENTRY_WITH_234_NUMBERS': 'Option B',
            '123443': 'Option C',
        }
        invalid_entries = {
            'CONFIG_ENtry_skipped': 'Option',
            'CONFIG_ENtry_$#': 'Option',
            # Empty
            '': 'Option',
        }
        for k, v in valid_entries.items():
            os.environ['%s%s' % (CFG_ENVIRO_ID, k)] = v
        for k, v in invalid_entries.items():
            os.environ['%s%s' % (CFG_ENVIRO_ID, k)] = v

        script = ScanScript()
        for k, v in valid_entries.items():
            assert k in script.config
            assert script.config[k] == v

        for k in invalid_entries.keys():
            assert k not in script.config

        # Cleanup
        for k, v in valid_entries.items():
            del os.environ['%s%s' % (CFG_ENVIRO_ID, k)]
        for k, v in invalid_entries.items():
            del os.environ['%s%s' % (CFG_ENVIRO_ID, k)]

    def test_nzbget_push_nzbname(self):

        # a NZB Logger set to False uses stderr
        script = ScanScript(logger=False, debug=VERY_VERBOSE_DEBUG)

        nzbname = '%s.but.with.more.content' % NZBNAME

        # Keep a handle on the real standard output
        stdout = sys.stdout
        sys.stdout = StringIO()
        script.push_nzbname(nzbname)

        # extract data
        sys.stdout.seek(0)
        output = sys.stdout.read().strip()

        # return stdout back to how it was
        sys.stdout = stdout
        assert output == '%s%s=%s' % (
            NZBGET_MSG_PREFIX,
            'NZBNAME',
            nzbname,
        )
        assert script.nzbname == nzbname
        assert script.system['NZBNAME'] == nzbname

    def test_nzbget_push_category(self):

        # a NZB Logger set to False uses stderr
        script = ScanScript(logger=False, debug=VERY_VERBOSE_DEBUG)

        category = '%s100' % CATEGORY

        # Keep a handle on the real standard output
        stdout = sys.stdout
        sys.stdout = StringIO()
        script.push_category(category)

        # extract data
        sys.stdout.seek(0)
        output = sys.stdout.read().strip()

        # return stdout back to how it was
        sys.stdout = stdout
        assert output == '%s%s=%s' % (
            NZBGET_MSG_PREFIX,
            'CATEGORY',
            category,
        )
        assert script.category == category
        assert script.system['CATEGORY'] == category

    def test_nzbget_push_priority(self):

        # a NZB Logger set to False uses stderr
        script = ScanScript(logger=False, debug=VERY_VERBOSE_DEBUG)

        priority = PRIORITY.FORCE

        # Keep a handle on the real standard output
        stdout = sys.stdout
        sys.stdout = StringIO()
        script.push_priority(priority)

        # extract data
        sys.stdout.seek(0)
        output = sys.stdout.read().strip()

        # return stdout back to how it was
        sys.stdout = stdout
        assert output == '%s%s=%d' % (
            NZBGET_MSG_PREFIX,
            'PRIORITY',
            priority,
        )
        assert script.priority == priority
        assert script.system['PRIORITY'] == priority

    def test_nzbget_push_top(self):

        # a NZB Logger set to False uses stderr
        script = ScanScript(logger=False, debug=VERY_VERBOSE_DEBUG)

        top = not TOP

        # Keep a handle on the real standard output
        stdout = sys.stdout
        sys.stdout = StringIO()
        script.push_top(top)

        # extract data
        sys.stdout.seek(0)
        output = sys.stdout.read().strip()

        # return stdout back to how it was
        sys.stdout = stdout
        assert output == '%s%s=%d' % (
            NZBGET_MSG_PREFIX,
            'TOP',
            int(top),
        )
        assert script.top == top
        assert script.system['TOP'] == top

    def test_nzbget_push_paused(self):

        # a NZB Logger set to False uses stderr
        script = ScanScript(logger=False, debug=VERY_VERBOSE_DEBUG)

        paused = not PAUSED

        # Keep a handle on the real standard output
        stdout = sys.stdout
        sys.stdout = StringIO()
        script.push_paused(paused)

        # extract data
        sys.stdout.seek(0)
        output = sys.stdout.read().strip()

        # return stdout back to how it was
        sys.stdout = stdout
        assert output == '%s%s=%d' % (
            NZBGET_MSG_PREFIX,
            'PAUSED',
            int(paused),
        )
        assert script.paused == paused
        assert script.system['PAUSED'] == paused
