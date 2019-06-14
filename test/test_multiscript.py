# -*- encoding: utf-8 -*-
#
# A Test Suite (for nose) for the MultiScripts
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

from nzbget.PostProcessScript import PostProcessScript
from nzbget.PostProcessScript import POSTPROC_ENVIRO_ID
from nzbget.ScanScript import ScanScript
from nzbget.ScanScript import SCAN_ENVIRO_ID
from nzbget.SchedulerScript import SchedulerScript
from nzbget.SchedulerScript import SCHEDULER_ENVIRO_ID
from nzbget.ScriptBase import SCRIPT_MODE
from nzbget.ScriptBase import EXIT_CODE
from nzbget.ScriptBase import SYS_ENVIRO_ID
from nzbget.Logger import VERY_VERBOSE_DEBUG


class TestPostProcessScript(TestBase):
    def setup_method(self):
        """This method is run once before _each_ test method is executed"""
        super(TestPostProcessScript, self).setup_method()

        if '%sDESTDIR' % SYS_ENVIRO_ID in os.environ:
            del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        if '%sDIRECTORY' % SCAN_ENVIRO_ID in os.environ:
            del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]
        if '%sDIRECTORY' % POSTPROC_ENVIRO_ID in os.environ:
            del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

    def teardown_method(self):
        """This method is run once after _each_ test method is executed"""
        # Eliminate any variables defined
        if '%sDESTDIR' % SYS_ENVIRO_ID in os.environ:
            del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        if '%sDIRECTORY' % SCAN_ENVIRO_ID in os.environ:
            del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]
        if '%sDIRECTORY' % POSTPROC_ENVIRO_ID in os.environ:
            del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

        # common
        super(TestPostProcessScript, self).teardown_method()

    def test_dual_script01(self):
        """
        Testing NZBGet Script initialization using environment variables
        """
        class TestDualScript(PostProcessScript, SchedulerScript):
            pass

        # No environment variables make us unsure what we're testing
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.NONE

        # Scheduler Sanity
        os.environ['%sTASKID' % SCHEDULER_ENVIRO_ID] = '1'
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.SCHEDULER
        del os.environ['%sTASKID' % SCHEDULER_ENVIRO_ID]

        # Scan Sanity
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.NONE
        del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]

        # PostProcess Sanity
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

        # Post Process still trumps all (if all are set)
        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

    def test_dual_script02(self):
        """
        Testing NZBGet Script initialization using environment variables
        Reversing them from test01 alters the initialization, but
        should not affect the end result
        """
        class TestDualScript(SchedulerScript, PostProcessScript):
            pass

        # No environment variables make us unsure what we're testing
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.NONE

        # Scheduler Sanity
        os.environ['%sTASKID' % SCHEDULER_ENVIRO_ID] = '1'
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.SCHEDULER
        del os.environ['%sTASKID' % SCHEDULER_ENVIRO_ID]

        # Scan Sanity
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.NONE
        del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]

        # PostProcess Sanity
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

        # Post Process still trumps all (if all are set)
        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

    def test_dual_script03(self):
        """
        Testing NZBGet Script initialization using environment variables
        Reversing them from test01 alters the initialization, but
        should not affect the end result
        """
        class TestDualScript(ScanScript, PostProcessScript):
            pass

        # No environment variables make us unsure what we're testing
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.NONE

        # Scheduler Sanity
        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.NONE
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]

        # Scan Sanity
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.SCAN
        del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]

        # PostProcess Sanity
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

        # Post Process still trumps all (if all are set)
        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

    def test_dual_force_script01(self):

        class TestDualScript(ScanScript, PostProcessScript):
            pass

        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG,
                                script_mode=SCRIPT_MODE.POSTPROCESSING)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING

        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG,
                                script_mode=SCRIPT_MODE.SCAN)
        assert script.detect_mode() == SCRIPT_MODE.SCAN

        # SchedulerScript is not part of DualScript, so therefore
        # it can't be foreced
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG,
                                script_mode=SCRIPT_MODE.SCHEDULER)
        assert script.detect_mode() == SCRIPT_MODE.NONE

        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG,
                                script_mode=SCRIPT_MODE.NONE)
        assert script.detect_mode() == SCRIPT_MODE.NONE

    def test_dual_force_script02(self):

        class TestDualScript(SchedulerScript, PostProcessScript):
            pass

        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG,
                                script_mode=SCRIPT_MODE.POSTPROCESSING)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING

        # ScanScript is not part of DualScript, so therefore
        # it can't be foreced
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG,
                                script_mode=SCRIPT_MODE.SCAN)
        assert script.detect_mode() == SCRIPT_MODE.NONE

        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG,
                                script_mode=SCRIPT_MODE.SCHEDULER)
        assert script.detect_mode() == SCRIPT_MODE.SCHEDULER

        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG,
                                script_mode=SCRIPT_MODE.NONE)
        assert script.detect_mode() == SCRIPT_MODE.NONE

    def test_dual_force_script03(self):

        class TestDualScript(SchedulerScript, ScanScript):
            pass

        # PostProcessingScript is not part of DualScript, so therefore
        # it can't be foreced
        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG,
                                script_mode=SCRIPT_MODE.POSTPROCESSING)
        assert script.detect_mode() == SCRIPT_MODE.NONE

        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG,
                                script_mode=SCRIPT_MODE.SCAN)
        assert script.detect_mode() == SCRIPT_MODE.SCAN

        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG,
                                script_mode=SCRIPT_MODE.SCHEDULER)
        assert script.detect_mode() == SCRIPT_MODE.SCHEDULER

        script = TestDualScript(logger=False, debug=VERY_VERBOSE_DEBUG,
                                script_mode=SCRIPT_MODE.NONE)
        assert script.detect_mode() == SCRIPT_MODE.NONE

    def test_tri_script01(self):
        """
        Testing NZBGet Script initialization using environment variables
        Reversing them from test01 alters the initialization, but
        should not affect the end result
        """
        class TestTriScript(SchedulerScript, PostProcessScript, ScanScript):
            pass

        # No environment variables make us unsure what we're testing
        script = TestTriScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.NONE

        # Scheduler Sanity
        os.environ['%sTASKID' % SCHEDULER_ENVIRO_ID] = '1'
        script = TestTriScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.SCHEDULER
        del os.environ['%sTASKID' % SCHEDULER_ENVIRO_ID]

        # Scan Sanity
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestTriScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.SCAN
        del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]

        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestTriScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.SCAN
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]

        # PostProcess Sanity
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestTriScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestTriScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

        # Post Process still trumps all (if all are set)
        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestTriScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

    def test_dual_run(self):
        class TestDualScript(SchedulerScript, PostProcessScript):
            def postprocess_main(self, *args, **kwargs):
                return None

            def scheduler_main(self, *args, **kwargs):
                return False

        script = TestDualScript(
            logger=False, debug=VERY_VERBOSE_DEBUG,
            script_mode=SCRIPT_MODE.POSTPROCESSING,
        )
        assert script.run() == EXIT_CODE.NONE

        script = TestDualScript(
            logger=False, debug=VERY_VERBOSE_DEBUG,
            script_mode=SCRIPT_MODE.SCHEDULER,
        )
        assert script.run() == EXIT_CODE.FAILURE
