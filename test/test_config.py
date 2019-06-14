# -*- encoding: utf-8 -*-
#
# A Test Suite (for nose) for the Config Tests Class
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
from os.path import join

from TestBase import TestBase
from TestBase import TEMP_DIRECTORY

from nzbget.ScriptBase import SYS_ENVIRO_ID
from nzbget.ScriptBase import TEST_COMMAND
from nzbget.ScriptBase import EXIT_CODE
from nzbget.ScriptBase import SHELL_EXIT_CODE
from nzbget.ScriptBase import SCRIPT_MODE
from nzbget.PostProcessScript import PostProcessScript

from nzbget.Logger import VERY_VERBOSE_DEBUG

# Some constants to work with
DIRECTORY = TEMP_DIRECTORY

# For validation
SCRIPTDIR = join(TEMP_DIRECTORY, 'scripts')

VERSION = 18


class TestConfigScript(TestBase):
    def setup_method(self):
        """This method is run once before _each_ test method is executed"""
        super(TestConfigScript, self).setup_method()

        # Create some environment variables
        os.environ['%sSCRIPTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sVERSION' % SYS_ENVIRO_ID] = str(VERSION)

    def teardown_method(self):
        """This method is run once after _each_ test method is executed"""
        # Eliminate any variables defined
        if '%sSCRIPTDIR' % SYS_ENVIRO_ID in os.environ:
            del os.environ['%sSCRIPTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sTEMPDIR' % SYS_ENVIRO_ID]
        del os.environ['%sVERSION' % SYS_ENVIRO_ID]

        # common
        super(TestConfigScript, self).teardown_method()

    def test_action_detection(self):
        """
        A Series of tests to show how the detection works
        """
        os.environ[TEST_COMMAND] = 'MyTestAction'

        class MyTestObj(PostProcessScript):
            # Definition = action_<name>
            def action_MyTestAction(self, *args, **kwargs):
                """
                Test object
                """
                return True

        # Create our Object
        obj = MyTestObj(
            logger=False,
            debug=VERY_VERBOSE_DEBUG,
        )

        assert(obj.script_mode == SCRIPT_MODE.CONFIG_ACTION)
        assert(obj.run() == EXIT_CODE.SUCCESS)

        # Now we try with the lower case version
        class MyTestObj(PostProcessScript):
            # Lower Case
            def action_mytestaction(self, *args, **kwargs):
                """
                Test object
                """
                return True

        # Create our Object
        obj = MyTestObj(
            logger=False,
            debug=VERY_VERBOSE_DEBUG,
        )

        assert(obj.run() == EXIT_CODE.SUCCESS)
        assert(obj.script_mode == SCRIPT_MODE.CONFIG_ACTION)

        # We do nothing if neither of these functions are present.
        # Now we try with the lower case version
        class MyTestObj(PostProcessScript):
            pass

        # Create our Object
        obj = MyTestObj(
            logger=False,
            debug=VERY_VERBOSE_DEBUG,
        )

        assert(obj.script_mode == SCRIPT_MODE.NONE)
        assert(obj.run() == SHELL_EXIT_CODE.SUCCESS)

        # If the environment variable doesn't exist at all
        # Then for sure we don't run either test function
        del os.environ[TEST_COMMAND]

        # Now we try with the lower case version
        class MyTestObj(PostProcessScript):
            # Lower Case
            def action_mytestaction(self, *args, **kwargs):
                """
                Test object
                """
                return True

            # Definition = action_<name>
            def action_MyTestAction(self, *args, **kwargs):
                """
                Test object
                """
                return True

        # Create our Object
        obj = MyTestObj(
            logger=False,
            debug=VERY_VERBOSE_DEBUG,
        )

        assert(obj.script_mode == SCRIPT_MODE.NONE)
        assert(obj.run() == SHELL_EXIT_CODE.SUCCESS)
