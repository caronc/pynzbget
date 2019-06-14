# -*- encoding: utf-8 -*-
#
# A Test Suite (for nose) for the FeedScript Class
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

from TestBase import TestBase
from TestBase import TEMP_DIRECTORY

from nzbget.ScriptBase import CFG_ENVIRO_ID
from nzbget.ScriptBase import SYS_ENVIRO_ID

from nzbget.FeedScript import FeedScript
from nzbget.FeedScript import FEED_ENVIRO_ID

from nzbget.Logger import VERY_VERBOSE_DEBUG

# Some constants to work with
FEEDID = "1"
FEED_FILENAME = 'MyTest.nzb'


class TestFeedScript(TestBase):
    def setup_method(self):
        """This method is run once before _each_ test method is executed"""
        super(TestFeedScript, self).setup_method()

        # Create some environment variables
        os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sFEEDID' % FEED_ENVIRO_ID] = FEEDID
        os.environ['%sFILENAME' % FEED_ENVIRO_ID] = FEED_FILENAME

    def teardown_method(self):
        """This method is run once after _each_ test method is executed"""
        # Eliminate any variables defined
        del os.environ['%sFEEDID' % FEED_ENVIRO_ID]
        del os.environ['%sFILENAME' % FEED_ENVIRO_ID]

        # common
        super(TestFeedScript, self).teardown_method()

    def test_environment_varable_init(self):
        """
        Testing NZBGet Script initialization using environment variables
        """
        # a NZB Logger set to False uses stderr
        script = FeedScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.feedid == int(FEEDID)
        assert script.filename == FEED_FILENAME

        assert script.system['FEEDID'] == int(FEEDID)
        assert script.system['FILENAME'] == FEED_FILENAME

        assert script.get('TEMPDIR') == TEMP_DIRECTORY
        assert script.get('FEEDID') == int(FEEDID)
        assert script.get('FILENAME') == FEED_FILENAME

        assert len(script.config) == 1
        assert script.config.get('DEBUG') == VERY_VERBOSE_DEBUG

        assert os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] == TEMP_DIRECTORY
        assert os.environ['%sFEEDID' % FEED_ENVIRO_ID] == FEEDID
        assert os.environ['%sFILENAME' % FEED_ENVIRO_ID] == FEED_FILENAME

    def test_environment_override(self):
        """
        Testing NZBGet Script initialization using forced variables that
        should take priority over global ones
        """
        feedid = int(FEEDID) + 1
        filename = 'TEST_OVERLOAD_%s' % FEED_FILENAME
        script = FeedScript(
            logger=False,
            debug=VERY_VERBOSE_DEBUG,
            feedid=feedid,
            filename=filename,
        )

        assert script.feedid == feedid

        assert script.system['TEMPDIR'] == TEMP_DIRECTORY
        assert script.system['FEEDID'] == feedid
        assert script.system['FILENAME'] == filename

        assert len(script.config) == 1
        assert script.config.get('DEBUG') == VERY_VERBOSE_DEBUG

        assert os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] == TEMP_DIRECTORY
        assert os.environ['%sFEEDID' % FEED_ENVIRO_ID] == str(feedid)
        assert os.environ['%sFILENAME' % FEED_ENVIRO_ID] == filename

    def test_get_feed(self):

        script = FeedScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        feed = script.get_feed()
        assert len(feed) == 0

    def test_set_and_get(self):
        # a NZB Logger set to False uses stderr
        script = FeedScript(logger=False, debug=VERY_VERBOSE_DEBUG)

        KEY = 'MY_VAR'
        VALUE = 'MY_VALUE'

        # Value does not exist yet
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

        script = FeedScript()
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
