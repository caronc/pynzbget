import os
from PostProcessScript import PostProcessScript
from PostProcessScript import POSTPROC_ENVIRO_ID
from ScanScript import ScanScript
from ScanScript import SCAN_ENVIRO_ID
from SchedulerScript import SchedulerScript
from ScriptBase import SCRIPT_MODE
from ScriptBase import SYS_ENVIRO_ID
from TestBase import TestBase
from TestBase import TEMP_DIRECTORY

class TestPostProcessScript(TestBase):
    def setUp(self):
        # common
        super(TestPostProcessScript, self).setUp()

        if '%sDESTDIR' % SYS_ENVIRO_ID in os.environ:
            del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        if '%sDIRECTORY' % SCAN_ENVIRO_ID in os.environ:
            del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]
        if '%sDIRECTORY' % POSTPROC_ENVIRO_ID in os.environ:
            del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

    def tearDown(self):
        # Eliminate any variables defined
        if '%sDESTDIR' % SYS_ENVIRO_ID in os.environ:
            del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        if '%sDIRECTORY' % SCAN_ENVIRO_ID in os.environ:
            del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]
        if '%sDIRECTORY' % POSTPROC_ENVIRO_ID in os.environ:
            del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

    def test_dual_script01(self):
        """
        Testing NZBGet Script initialization using environment variables
        """
        class TestDualScript(PostProcessScript, SchedulerScript):
            pass

        print os.environ.keys()
        # No environment variables make us unsure what we're testing
        script = TestDualScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.NONE

        # Scheduler Sanity
        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.SCHEDULER
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]

        # Scan Sanity
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.NONE
        del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]

        # PostProcess Sanity
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

        # Post Process still trumps all (if all are set)
        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=True)
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
        script = TestDualScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.NONE

        # Scheduler Sanity
        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.SCHEDULER
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]

        # Scan Sanity
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.NONE
        del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]

        # PostProcess Sanity
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

        # Post Process still trumps all (if all are set)
        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=True)
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
        script = TestDualScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.NONE

        # Scheduler Sanity
        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.NONE
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]

        # Scan Sanity
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.SCAN
        del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]

        # PostProcess Sanity
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

        # Post Process still trumps all (if all are set)
        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestDualScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

    def test_dual_force_script01(self):

        class TestDualScript(ScanScript, PostProcessScript):
            pass

        script = TestDualScript(logger=False, debug=True,
                                script_mode=SCRIPT_MODE.POSTPROCESSING)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING

        script = TestDualScript(logger=False, debug=True,
                                script_mode=SCRIPT_MODE.SCAN)
        assert script.detect_mode() == SCRIPT_MODE.SCAN

        # SchedulerScript is not part of DualScript, so therefore
        # it can't be foreced
        script = TestDualScript(logger=False, debug=True,
                                script_mode=SCRIPT_MODE.SCHEDULER)
        assert script.detect_mode() == SCRIPT_MODE.NONE

        script = TestDualScript(logger=False, debug=True,
                                script_mode=SCRIPT_MODE.NONE)
        assert script.detect_mode() == SCRIPT_MODE.NONE

    def test_dual_force_script02(self):

        class TestDualScript(SchedulerScript, PostProcessScript):
            pass

        script = TestDualScript(logger=False, debug=True,
                                script_mode=SCRIPT_MODE.POSTPROCESSING)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING

        # ScanScript is not part of DualScript, so therefore
        # it can't be foreced
        script = TestDualScript(logger=False, debug=True,
                                script_mode=SCRIPT_MODE.SCAN)
        assert script.detect_mode() == SCRIPT_MODE.NONE

        script = TestDualScript(logger=False, debug=True,
                                script_mode=SCRIPT_MODE.SCHEDULER)
        assert script.detect_mode() == SCRIPT_MODE.SCHEDULER

        script = TestDualScript(logger=False, debug=True,
                                script_mode=SCRIPT_MODE.NONE)
        assert script.detect_mode() == SCRIPT_MODE.NONE

    def test_dual_force_script03(self):

        class TestDualScript(SchedulerScript, ScanScript):
            pass

        # PostProcessingScript is not part of DualScript, so therefore
        # it can't be foreced
        script = TestDualScript(logger=False, debug=True,
                                script_mode=SCRIPT_MODE.POSTPROCESSING)
        assert script.detect_mode() == SCRIPT_MODE.NONE

        script = TestDualScript(logger=False, debug=True,
                                script_mode=SCRIPT_MODE.SCAN)
        assert script.detect_mode() == SCRIPT_MODE.SCAN

        script = TestDualScript(logger=False, debug=True,
                                script_mode=SCRIPT_MODE.SCHEDULER)
        assert script.detect_mode() == SCRIPT_MODE.SCHEDULER

        script = TestDualScript(logger=False, debug=True,
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
        script = TestTriScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.NONE

        # Scheduler Sanity
        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestTriScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.SCHEDULER
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]

        # Scan Sanity
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestTriScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.SCAN
        del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]

        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestTriScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.SCAN
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]

        # PostProcess Sanity
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestTriScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestTriScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]

        # Post Process still trumps all (if all are set)
        os.environ['%sDESTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = TEMP_DIRECTORY
        script = TestTriScript(logger=False, debug=True)
        assert script.detect_mode() == SCRIPT_MODE.POSTPROCESSING
        del os.environ['%sDESTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % SCAN_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]
