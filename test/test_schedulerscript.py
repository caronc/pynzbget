# -*- encoding: utf-8 -*-
#
# A Test Suite (for nose) for the SchedulerScript Class
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
from nzbget.SchedulerScript import SchedulerScript
from nzbget.SchedulerScript import SCHEDULER_ENVIRO_ID
from nzbget.SchedulerScript import TASK_ENVIRO_ID

from nzbget.Logger import VERY_VERBOSE_DEBUG

# Some constants to work with
TASKID = "1"
TASK_PARAM = 'MyScript.py'
TASK_TIME = '00:00,00:15'


class TestSchedulerScript(TestBase):
    def setup_method(self):
        """This method is run once before _each_ test method is executed"""
        super(TestSchedulerScript, self).setup_method()

        # Create some environment variables
        os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sTASKID' % SCHEDULER_ENVIRO_ID] = TASKID
        os.environ['%s%s%s_PARAM' % (
            SCHEDULER_ENVIRO_ID, TASK_ENVIRO_ID, TASKID)] = TASK_PARAM
        os.environ['%s%s%s_TIME' % (
            SCHEDULER_ENVIRO_ID, TASK_ENVIRO_ID, TASKID)] = TASK_TIME

    def teardown_method(self):
        """This method is run once after _each_ test method is executed"""
        # Eliminate any variables defined
        del os.environ['%sTASKID' % SCHEDULER_ENVIRO_ID]
        del os.environ['%s%s%s_PARAM' % (
            SCHEDULER_ENVIRO_ID, TASK_ENVIRO_ID, TASKID)]
        del os.environ['%s%s%s_TIME' % (
            SCHEDULER_ENVIRO_ID, TASK_ENVIRO_ID, TASKID)]

        # common
        super(TestSchedulerScript, self).teardown_method()

    def test_environment_varable_init(self):
        """
        Testing NZBGet Script initialization using environment variables
        """
        # a NZB Logger set to False uses stderr
        script = SchedulerScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.taskid == int(TASKID)

        assert script.system['TASKID'] == int(TASKID)
        assert script.system['%s%s_PARAM' % (
            TASK_ENVIRO_ID, TASKID)] == TASK_PARAM
        assert script.system['%s%s_TIME' % (
            TASK_ENVIRO_ID, TASKID)] == TASK_TIME

        assert script.get('TEMPDIR') == TEMP_DIRECTORY
        assert script.get('TASKID') == int(TASKID)
        assert script.get('%s%s_PARAM' % (
            TASK_ENVIRO_ID, TASKID)) == TASK_PARAM
        assert script.get('%s%s_TIME' % (
            TASK_ENVIRO_ID, TASKID)) == TASK_TIME

        assert len(script.config) == 1
        assert script.config.get('DEBUG') == VERY_VERBOSE_DEBUG

        assert os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] == TEMP_DIRECTORY
        assert os.environ['%sTASKID' % SCHEDULER_ENVIRO_ID] == TASKID
        assert os.environ['%s%s%s_PARAM' % (
            SCHEDULER_ENVIRO_ID, TASK_ENVIRO_ID, TASKID)] == TASK_PARAM
        assert os.environ['%s%s%s_TIME' % (
            SCHEDULER_ENVIRO_ID, TASK_ENVIRO_ID, TASKID)] == TASK_TIME

    def test_environment_override(self):
        """
        Testing NZBGet Script initialization using forced variables that
        should take priority over global ones
        """
        taskid = int(TASKID) + 1
        script = SchedulerScript(
            logger=False,
            debug=VERY_VERBOSE_DEBUG,

            taskid=taskid,
        )

        assert script.taskid == taskid

        assert script.system['TEMPDIR'] == TEMP_DIRECTORY
        assert script.system['TASKID'] == taskid

        assert len(script.config) == 1
        assert script.config.get('DEBUG') == VERY_VERBOSE_DEBUG

        assert os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] == TEMP_DIRECTORY
        assert os.environ['%sTASKID' % SCHEDULER_ENVIRO_ID] == str(taskid)

    def test_get_task(self):
        script = SchedulerScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        task = script.get_task()
        assert len(task) == 2

    def test_set_and_get(self):
        # a NZB Logger set to False uses stderr
        script = SchedulerScript(logger=False, debug=VERY_VERBOSE_DEBUG)

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

        script = SchedulerScript()
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
