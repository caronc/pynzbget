# -*- encoding: utf-8 -*-
#
# A Test Suite (for nose) for the SABnzbd SABPostProcessScript Class
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
from os import makedirs
from os.path import basename
from os.path import dirname
from os.path import isfile
from os.path import join

from TestBase import TestBase
from TestBase import TEMP_DIRECTORY

from nzbget.ScriptBase import SAB_ENVIRO_ID
from nzbget.ScriptBase import SHELL_EXIT_CODE

from nzbget.SABPostProcessScript import SABPostProcessScript
from nzbget.SABPostProcessScript import PP_STATUS
from nzbget.Logger import VERY_VERBOSE_DEBUG


from shutil import rmtree

# Some constants to work with
DIRECTORY = TEMP_DIRECTORY
COMPLETE_DIRECTORY = TEMP_DIRECTORY
NZBNAME = 'A.Great.Movie'
NZBFILENAME = join(TEMP_DIRECTORY, 'A.Great.Movie.nzb')
CATEGORY = 'movie'
VERSION = '2.1'
SEARCH_DIR = join(TEMP_DIRECTORY, 'file_listing')

# For validation
STATUS = str(PP_STATUS.SUCCESS)


class TestSABPostProcessScript(TestBase):
    def setup_method(self):
        """This method is run once before _each_ test method is executed"""
        super(TestSABPostProcessScript, self).setup_method()

        # Create NZBFILE
        _f = open(NZBFILENAME, 'w')
        _f.write("""<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE nzb PUBLIC "-//newzBin//DTD NZB 1.1//EN" "http://www.newzbin.com/DTD/nzb/nzb-1.1.dtd">
            <nzb xmlns="http://www.newzbin.com/DTD/2003/nzb">

            <head>
             <meta type="category">Movies &gt; SD</meta>
             <meta type="name">A.Great.Movie.1983.DVDRip.x264-AWESOME</meta>
             <meta type="propername">A Great Movie</meta>
             <meta type="movieyear">1983</meta>
            <!-- extra record used to determine what file we're reading -->
             <meta type="letter">A</meta>
            </head>
          </nzb>""")
        _f.close()

        # Create some environment variables
        os.environ['%sTEMPDIR' % SAB_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sVERSION' % SAB_ENVIRO_ID] = str(VERSION)
        os.environ['%sDIRECTORY' % SAB_ENVIRO_ID] = DIRECTORY
        os.environ['%sCOMPLETE_DIR' % SAB_ENVIRO_ID] = COMPLETE_DIRECTORY
        os.environ['%sNZBNAME' % SAB_ENVIRO_ID] = NZBFILENAME
        os.environ['%sFILENAME' % SAB_ENVIRO_ID] = NZBNAME
        os.environ['%sCAT' % SAB_ENVIRO_ID] = CATEGORY
        os.environ['%sPP_STATUS' % SAB_ENVIRO_ID] = STATUS

        # ensure directory doesn't exist
        try:
            rmtree(SEARCH_DIR)
        except:
            pass
        makedirs(SEARCH_DIR)

    def teardown_method(self):
        """This method is run once after _each_ test method is executed"""
        # Eliminate any variables defined
        del os.environ['%sTEMPDIR' % SAB_ENVIRO_ID]
        if '%sVERSION' % SAB_ENVIRO_ID in os.environ:
            del os.environ['%sVERSION' % SAB_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % SAB_ENVIRO_ID]
        del os.environ['%sNZBNAME' % SAB_ENVIRO_ID]
        if '%sCOMPLETED_DIR' % SAB_ENVIRO_ID in os.environ:
            del os.environ['%sCOMPLETED_DIR' % SAB_ENVIRO_ID]
        del os.environ['%sCAT' % SAB_ENVIRO_ID]
        del os.environ['%sPP_STATUS' % SAB_ENVIRO_ID]

        try:
            rmtree(SEARCH_DIR)
        except:
            pass

        # common
        super(TestSABPostProcessScript, self).teardown_method()

    def test_main_returns(self):
        # a NZB Logger set to False uses stderr
        script = SABPostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.run() == SHELL_EXIT_CODE.SUCCESS

        class TestSABPostProcessMain(SABPostProcessScript):
            def sabnzbd_postprocess_main(self, *args, **kwargs):
                return None

        script = TestSABPostProcessMain(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.run() == SHELL_EXIT_CODE.NONE

        del script
        # However we always pass in we validate our environment correctly
        script = SABPostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.run() == SHELL_EXIT_CODE.SUCCESS

        # If we fail to validate, then we flat out fail
        del os.environ['%sVERSION' % SAB_ENVIRO_ID]
        script = SABPostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.run() == SHELL_EXIT_CODE.FAILURE

    def test_environment_varable_init(self):
        """
        Testing NZBGet Script initialization using environment variables
        """
        # a NZB Logger set to False uses stderr
        script = SABPostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.directory == DIRECTORY
        assert script.nzbname == NZBNAME
        assert script.nzbfilename == NZBFILENAME
        assert script.category == CATEGORY

        assert script.system['TEMPDIR'] == TEMP_DIRECTORY
        assert script.system['VERSION'] == str(VERSION)
        assert script.system['DIRECTORY'] == DIRECTORY
        assert script.system['COMPLETE_DIR'] == COMPLETE_DIRECTORY
        assert script.system['FILENAME'] == NZBNAME
        assert script.system['NZBNAME'] == NZBFILENAME
        assert script.system['CAT'] == CATEGORY
        assert script.system['PP_STATUS'] == STATUS

        assert script.get('TEMPDIR') == TEMP_DIRECTORY
        assert script.get('VERSION') == str(VERSION)
        assert script.get('DIRECTORY') == DIRECTORY
        assert script.get('COMPLETE_DIR') == COMPLETE_DIRECTORY
        assert script.get('FILENAME') == NZBNAME
        assert script.get('NZBNAME') == NZBFILENAME
        assert script.get('CAT') == CATEGORY
        assert script.get('PP_STATUS') == STATUS

        assert len(script.config) == 1
        assert script.config.get('DEBUG') == VERY_VERBOSE_DEBUG

        assert script.nzbheaders['MOVIEYEAR'] == '1983'
        assert script.nzbheaders['NAME'] == \
            'A.Great.Movie.1983.DVDRip.x264-AWESOME'
        assert script.nzbheaders['PROPERNAME'] == 'A Great Movie'
        assert script.nzbheaders['CATEGORY'] == 'Movies > SD'

        assert script.nzb_get('movieyear') == '1983'
        assert script.nzb_get('name') == \
            'A.Great.Movie.1983.DVDRip.x264-AWESOME'
        assert script.nzb_get('propername') == 'A Great Movie'
        assert script.nzb_get('category') == 'Movies > SD'

        assert os.environ['%sTEMPDIR' % SAB_ENVIRO_ID] == TEMP_DIRECTORY
        assert os.environ['%sDIRECTORY' % SAB_ENVIRO_ID] == DIRECTORY
        assert os.environ['%sCOMPLETE_DIR' % SAB_ENVIRO_ID] == COMPLETE_DIRECTORY
        assert os.environ['%sFILENAME' % SAB_ENVIRO_ID] == NZBNAME
        assert os.environ['%sNZBNAME' % SAB_ENVIRO_ID] == NZBFILENAME
        assert os.environ['%sCAT' % SAB_ENVIRO_ID] == CATEGORY
        assert os.environ['%sPP_STATUS' % SAB_ENVIRO_ID] == STATUS

    def test_environment_override(self):
        """
        Testing NZBGet Script initialization using forced variables that
        should take priority over global ones
        """
        directory = join(DIRECTORY, 'a', 'deeper', 'path')
        # ensure directory doesn't exist
        try:
            rmtree(directory)
        except:
            pass
        makedirs(directory)

        nzbname = '%s.with.more.content' % NZBNAME
        nzbfilename = join(directory, basename(NZBFILENAME))
        category = '%s2' % CATEGORY
        status = str(PP_STATUS.FAILURE)

        script = SABPostProcessScript(
            logger=False,
            debug=VERY_VERBOSE_DEBUG,

            directory=directory,
            nzbname=nzbname,
            nzbfilename=nzbfilename,
            category=category,
            status=status,
        )

        assert script.directory == directory
        assert script.nzbname == nzbname
        assert script.nzbfilename == nzbfilename
        assert script.category == category
        assert str(script.status) == status

        assert script.system['TEMPDIR'] == TEMP_DIRECTORY
        assert script.system['DIRECTORY'] == directory
        assert script.system['FILENAME'] == nzbname
        assert script.system['NZBNAME'] == nzbfilename
        assert script.system['CAT'] == category
        assert script.system['PP_STATUS'] == status

        assert len(script.config) == 1
        assert script.config.get('DEBUG') == VERY_VERBOSE_DEBUG
        assert script.shared == {}
        assert script.nzbheaders == {}

        assert os.environ['%sTEMPDIR' % SAB_ENVIRO_ID] == TEMP_DIRECTORY
        assert os.environ['%sDIRECTORY' % SAB_ENVIRO_ID] == directory
        assert os.environ['%sFILENAME' % SAB_ENVIRO_ID] == nzbname
        assert os.environ['%sNZBNAME' % SAB_ENVIRO_ID] == nzbfilename
        assert os.environ['%sCAT' % SAB_ENVIRO_ID] == category
        assert os.environ['%sPP_STATUS' % SAB_ENVIRO_ID] == status

        # cleanup
        try:
            rmtree(directory)
        except:
            pass

    def test_validation(self):

        # This will fail because it's looking for the VERSION
        # variable defined with SABnzbd v2.1
        # a NZB Logger set to False uses stderr
        if '%sVERSION' % SAB_ENVIRO_ID in os.environ:
            del os.environ['%sVERSION' % SAB_ENVIRO_ID]
        script = SABPostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert not script.validate()
        del script

        # Now let's set it and try again
        os.environ['%sVERSION' % SAB_ENVIRO_ID] = VERSION
        # a NZB Logger set to False uses stderr
        script = SABPostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.validate()
        del script

        # Now we'll try arguments
        os.environ['%sVALUE_A' % SAB_ENVIRO_ID] = 'A'
        os.environ['%sVALUE_B' % SAB_ENVIRO_ID] = 'B'
        os.environ['%sVALUE_C' % SAB_ENVIRO_ID] = 'C'

        # a NZB Logger set to False uses stderr
        script = SABPostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.validate(keys=(
            'Value_A', 'VALUE_B', 'value_c'
        ))
        del os.environ['%sVALUE_A' % SAB_ENVIRO_ID]
        del os.environ['%sVALUE_B' % SAB_ENVIRO_ID]
        del os.environ['%sVALUE_C' % SAB_ENVIRO_ID]

    def test_gzipped_nzbfiles(self):
        """
        Test gziped nzbfiles
        """
        os.environ['%sORIG_NZB_GZ' % SAB_ENVIRO_ID] = join(
            dirname(__file__), 'var', 'plain.nzb.gz')

        # Create our object
        script = SABPostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)

        # We have a temporary file now
        tmp_file = script._sab_temp_nzb
        assert(isfile(tmp_file) is True)

        # Running our script will just return zero
        assert(script.run() == 0)

        # But not after we exit, our tmp_file would have been cleaned up
        assert(isfile(tmp_file) is False)

        # We should be able to uncompress this file

        del os.environ['%sORIG_NZB_GZ' % SAB_ENVIRO_ID]
