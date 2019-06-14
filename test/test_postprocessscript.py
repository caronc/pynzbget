# -*- encoding: utf-8 -*-
#
# A Test Suite (for nose) for the PostProcessScript Class
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
import re
from os import makedirs
from os.path import basename
from os.path import join
from os.path import splitext

from TestBase import TestBase
from TestBase import TEMP_DIRECTORY

from nzbget.ScriptBase import CFG_ENVIRO_ID
from nzbget.ScriptBase import SYS_ENVIRO_ID
from nzbget.ScriptBase import PUSH_ENVIRO_ID
from nzbget.ScriptBase import NZBGET_MSG_PREFIX
from nzbget.ScriptBase import SHR_ENVIRO_GUESS_ID
from nzbget.ScriptBase import EXIT_CODE
from nzbget.ScriptBase import Health

from nzbget.PostProcessScript import PostProcessScript
from nzbget.PostProcessScript import POSTPROC_ENVIRO_ID
from nzbget.PostProcessCommon import SCRIPT_STATUS
from nzbget.PostProcessScript import TOTAL_STATUS
from nzbget.PostProcessScript import PAR_STATUS
from nzbget.PostProcessScript import UNPACK_STATUS

from nzbget.Logger import VERY_VERBOSE_DEBUG

try:
    # Python v2.7
    from StringIO import StringIO
except ImportError:
    # Python v3.x
    from io import StringIO

from shutil import rmtree

# Some constants to work with
DIRECTORY = TEMP_DIRECTORY
NZBNAME = 'A.Great.Movie'
NZBFILENAME = join(TEMP_DIRECTORY, 'A.Great.Movie.nzb')
NZBFILENAME_SHOW_A = join(TEMP_DIRECTORY, 'A.Great.TV.Show.nzb')
NZBFILENAME_SHOW_B = join(TEMP_DIRECTORY, 'Another.Great.TV.Show.nzb')
CATEGORY = 'movie'
TOTALSTATUS = TOTAL_STATUS.SUCCESS
SCRIPTSTATUS = SCRIPT_STATUS.SUCCESS
STATUS = 'SUCCESS/ALL'
PARSTATUS = PAR_STATUS.SUCCESS
UNPACKSTATUS = UNPACK_STATUS.SUCCESS
VERSION = 13

SEARCH_DIR = join(TEMP_DIRECTORY, 'file_listing')

# For validation
SCRIPTDIR = join(TEMP_DIRECTORY, 'scripts')


class TestPostProcessScript(TestBase):
    def setup_method(self):
        """This method is run once before _each_ test method is executed"""
        super(TestPostProcessScript, self).setup_method()

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

        _f = open(NZBFILENAME_SHOW_A, 'w')
        _f.write("""<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE nzb PUBLIC "-//newzBin//DTD NZB 1.1//EN" "http://www.newzbin.com/DTD/nzb/nzb-1.1.dtd">
            <nzb xmlns="http://www.newzbin.com/DTD/2003/nzb">

            <head>
             <meta type="category">TV &gt; HD</meta>
             <meta type="name">A.Great.TV.Show.S04E06.720p.HDTV.x264-AWESOME</meta>
             <meta type="propername">A Great TV Show</meta>
             <meta type="episodename">An Amazing Episode Name</meta>
            <!-- extra record used to determine what file we're reading -->
             <meta type="letter">B</meta>
            </head>
          </nzb>""")
        _f.close()

        _f = open('%s.queued' % NZBFILENAME_SHOW_A, 'w')
        _f.write("""<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE nzb PUBLIC "-//newzBin//DTD NZB 1.1//EN" "http://www.newzbin.com/DTD/nzb/nzb-1.1.dtd">
            <nzb xmlns="http://www.newzbin.com/DTD/2003/nzb">

            <head>
             <meta type="category">TV &gt; HD</meta>
             <meta type="name">A.Great.TV.Show.S04E06.720p.HDTV.x264-AWESOME</meta>
             <meta type="propername">A Great TV Show</meta>
             <meta type="episodename">An Amazing Episode Name</meta>
            <!-- extra record used to determine what file we're reading -->
             <meta type="letter">C</meta>
            </head>
          </nzb>""")
        _f.close()

        _f = open('%s' % NZBFILENAME_SHOW_B, 'w')
        _f.write("""<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE nzb PUBLIC "-//newzBin//DTD NZB 1.1//EN" "http://www.newzbin.com/DTD/nzb/nzb-1.1.dtd">
            <nzb xmlns="http://www.newzbin.com/DTD/2003/nzb">

            <head>
             <meta type="category">TV &gt; HD</meta>
             <meta type="name">Another.Great.TV.Show.S01E02.720p.HDTV.x264-AWESOME</meta>
             <meta type="propername">Another Great TV Show</meta>
             <meta type="episodename">An Okay Episode Name</meta>
            <!-- extra record used to determine what file we're reading -->
             <meta type="letter">D</meta>
            </head>
          </nzb>""")
        _f.close()

        _f = open('%s.queued' % NZBFILENAME_SHOW_B, 'w')
        _f.write("""<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE nzb PUBLIC "-//newzBin//DTD NZB 1.1//EN" "http://www.newzbin.com/DTD/nzb/nzb-1.1.dtd">
            <nzb xmlns="http://www.newzbin.com/DTD/2003/nzb">

            <head>
             <meta type="category">TV &gt; HD</meta>
             <meta type="name">Another.Great.TV.Show.S01E02.720p.HDTV.x264-AWESOME</meta>
             <meta type="propername">Another Great TV Show</meta>
             <meta type="episodename">An Okay Episode Name</meta>
            <!-- extra record used to determine what file we're reading -->
             <meta type="letter">E</meta>
            </head>
          </nzb>""")
        _f.close()

        _f = open('%s.2.queued' % NZBFILENAME_SHOW_B, 'w')
        _f.write("""<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE nzb PUBLIC "-//newzBin//DTD NZB 1.1//EN" "http://www.newzbin.com/DTD/nzb/nzb-1.1.dtd">
            <nzb xmlns="http://www.newzbin.com/DTD/2003/nzb">

            <head>
             <meta type="category">TV &gt; HD</meta>
             <meta type="name">Another.Great.TV.Show.S01E02.720p.HDTV.x264-AWESOME</meta>
             <meta type="propername">Another Great TV Show</meta>
             <meta type="episodename">An Okay Episode Name</meta>
            <!-- extra record used to determine what file we're reading -->
             <meta type="letter">F</meta>
            </head>
          </nzb>""")
        _f.close()

        # Create some environment variables
        os.environ['%sSCRIPTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sVERSION' % SYS_ENVIRO_ID] = str(VERSION)
        os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] = DIRECTORY
        os.environ['%sNZBNAME' % POSTPROC_ENVIRO_ID] = NZBNAME
        os.environ['%sNZBFILENAME' % POSTPROC_ENVIRO_ID] = NZBFILENAME
        os.environ['%sCATEGORY' % POSTPROC_ENVIRO_ID] = CATEGORY
        os.environ['%sTOTALSTATUS' % POSTPROC_ENVIRO_ID] = TOTALSTATUS
        os.environ['%sSTATUS' % POSTPROC_ENVIRO_ID] = STATUS
        os.environ['%sSCRIPTSTATUS' % POSTPROC_ENVIRO_ID] = SCRIPTSTATUS
        # NZBGet v11 support
        os.environ['%sPARSTATUS' % POSTPROC_ENVIRO_ID] = str(PARSTATUS)
        os.environ['%sUNPACKSTATUS' % POSTPROC_ENVIRO_ID] = str(UNPACKSTATUS)

        # ensure directory doesn't exist
        try:
            rmtree(SEARCH_DIR)
        except:
            pass
        makedirs(SEARCH_DIR)

    def teardown_method(self):
        """This method is run once after _each_ test method is executed"""
        # Eliminate any variables defined
        if '%sSCRIPTDIR' % SYS_ENVIRO_ID in os.environ:
            del os.environ['%sSCRIPTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sTEMPDIR' % SYS_ENVIRO_ID]
        del os.environ['%sVERSION' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]
        del os.environ['%sNZBNAME' % POSTPROC_ENVIRO_ID]
        del os.environ['%sNZBFILENAME' % POSTPROC_ENVIRO_ID]
        del os.environ['%sCATEGORY' % POSTPROC_ENVIRO_ID]
        del os.environ['%sTOTALSTATUS' % POSTPROC_ENVIRO_ID]
        del os.environ['%sSCRIPTSTATUS' % POSTPROC_ENVIRO_ID]
        del os.environ['%sPARSTATUS' % POSTPROC_ENVIRO_ID]
        del os.environ['%sUNPACKSTATUS' % POSTPROC_ENVIRO_ID]

        try:
            rmtree(SEARCH_DIR)
        except:
            pass

        # common
        super(TestPostProcessScript, self).teardown_method()

    def test_main_returns(self):
        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.run() == EXIT_CODE.SUCCESS

        class TestPostProcessMain(PostProcessScript):
            def postprocess_main(self, *args, **kwargs):
                return None

        script = TestPostProcessMain(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.run() == EXIT_CODE.NONE

        del script
        del os.environ['%sSCRIPTDIR' % SYS_ENVIRO_ID]
        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.run() == EXIT_CODE.FAILURE

    def test_environment_varable_init(self):
        """
        Testing NZBGet Script initialization using environment variables
        """
        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.directory == DIRECTORY
        assert script.nzbname == NZBNAME
        assert script.nzbfilename == NZBFILENAME
        assert script.category == CATEGORY
        assert script.totalstatus == TOTALSTATUS
        assert str(script.status) == STATUS
        assert script.scriptstatus == SCRIPTSTATUS
        assert script.parstatus == PARSTATUS
        assert script.unpackstatus == UNPACKSTATUS

        assert script.system['TEMPDIR'] == TEMP_DIRECTORY
        assert script.system['VERSION'] == str(VERSION)
        assert script.system['DIRECTORY'] == DIRECTORY
        assert script.system['NZBNAME'] == NZBNAME
        assert script.system['NZBFILENAME'] == NZBFILENAME
        assert script.system['CATEGORY'] == CATEGORY
        assert script.system['TOTALSTATUS'] == TOTALSTATUS
        assert script.system['STATUS'] == STATUS
        assert script.system['SCRIPTSTATUS'] == SCRIPTSTATUS
        assert script.system['PARSTATUS'] == PARSTATUS
        assert script.system['UNPACKSTATUS'] == UNPACKSTATUS

        assert script.get('TEMPDIR') == TEMP_DIRECTORY
        assert script.get('VERSION') == str(VERSION)
        assert script.get('DIRECTORY') == DIRECTORY
        assert script.get('NZBNAME') == NZBNAME
        assert script.get('NZBFILENAME') == NZBFILENAME
        assert script.get('CATEGORY') == CATEGORY
        assert script.get('TOTALSTATUS') == TOTALSTATUS
        assert script.get('STATUS') == STATUS
        assert script.get('SCRIPTSTATUS') == SCRIPTSTATUS
        assert script.get('PARSTATUS') == PARSTATUS
        assert script.get('UNPACKSTATUS') == UNPACKSTATUS

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

        assert os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] == TEMP_DIRECTORY
        assert os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] == DIRECTORY
        assert os.environ['%sNZBNAME' % POSTPROC_ENVIRO_ID] == NZBNAME
        assert os.environ['%sNZBFILENAME' % POSTPROC_ENVIRO_ID] == NZBFILENAME
        assert os.environ['%sCATEGORY' % POSTPROC_ENVIRO_ID] == CATEGORY
        assert os.environ['%sTOTALSTATUS' % POSTPROC_ENVIRO_ID] == TOTALSTATUS
        assert os.environ['%sSTATUS' % POSTPROC_ENVIRO_ID] == STATUS
        assert os.environ['%sSCRIPTSTATUS' % POSTPROC_ENVIRO_ID] == \
            SCRIPTSTATUS
        assert os.environ['%sPARSTATUS' % POSTPROC_ENVIRO_ID] == str(PARSTATUS)
        assert os.environ['%sUNPACKSTATUS' % POSTPROC_ENVIRO_ID] == \
            str(UNPACKSTATUS)

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
        totalstatus = TOTAL_STATUS.DELETED
        scriptstatus = SCRIPT_STATUS.FAILURE
        status = 'FAILURE/UNPACK'
        parstatus = PAR_STATUS.FAILURE
        unpackstatus = UNPACK_STATUS.FAILURE

        script = PostProcessScript(
            logger=False,
            debug=VERY_VERBOSE_DEBUG,

            directory=directory,
            nzbname=nzbname,
            nzbfilename=nzbfilename,
            category=category,
            totalstatus=totalstatus,
            status=status,
            scriptstatus=scriptstatus,

            # v11 Support
            parstatus=parstatus,
            unpackstatus=unpackstatus,
        )

        assert script.directory == directory
        assert script.nzbname == nzbname
        assert script.nzbfilename == nzbfilename
        assert script.category == category
        assert script.totalstatus == totalstatus
        assert str(script.status) == status
        assert script.scriptstatus == scriptstatus
        assert script.parstatus == parstatus
        assert script.unpackstatus == unpackstatus

        assert script.system['TEMPDIR'] == TEMP_DIRECTORY
        assert script.system['DIRECTORY'] == directory
        assert script.system['NZBNAME'] == nzbname
        assert script.system['NZBFILENAME'] == nzbfilename
        assert script.system['CATEGORY'] == category
        assert script.system['TOTALSTATUS'] == totalstatus
        assert script.system['STATUS'] == status
        assert script.system['SCRIPTSTATUS'] == scriptstatus
        assert script.system['PARSTATUS'] == parstatus
        assert script.system['UNPACKSTATUS'] == unpackstatus

        assert len(script.config) == 1
        assert script.config.get('DEBUG') == VERY_VERBOSE_DEBUG
        assert script.shared == {}
        assert script.nzbheaders == {}

        assert os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] == TEMP_DIRECTORY
        assert os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID] == directory
        assert os.environ['%sNZBNAME' % POSTPROC_ENVIRO_ID] == nzbname
        assert os.environ['%sNZBFILENAME' % POSTPROC_ENVIRO_ID] == nzbfilename
        assert os.environ['%sCATEGORY' % POSTPROC_ENVIRO_ID] == category
        assert os.environ['%sTOTALSTATUS' % POSTPROC_ENVIRO_ID] == totalstatus
        assert os.environ['%sSTATUS' % POSTPROC_ENVIRO_ID] == status
        assert os.environ['%sSCRIPTSTATUS' % POSTPROC_ENVIRO_ID] == \
            scriptstatus
        assert os.environ['%sPARSTATUS' % POSTPROC_ENVIRO_ID] == \
            str(parstatus)
        assert os.environ['%sUNPACKSTATUS' % POSTPROC_ENVIRO_ID] == \
            str(unpackstatus)

        # cleanup
        try:
            rmtree(directory)
        except:
            pass

    def test_set_and_get(self):
        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)

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

        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
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

    def test_nzbget_push_directory(self):

        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)

        directory = join(DIRECTORY, 'new', 'path')

        # Keep a handle on the real standard output
        stdout = sys.stdout
        sys.stdout = StringIO()
        script.push_directory(directory)

        # extract data
        sys.stdout.seek(0)
        output = sys.stdout.read().strip()

        # return stdout back to how it was
        sys.stdout = stdout
        assert output == '%s%s=%s' % (
            NZBGET_MSG_PREFIX,
            'DIRECTORY',
            directory,
        )
        assert script.directory == directory
        assert script.system['DIRECTORY'] == directory

    def test_nzbget_push_final_directory(self):

        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)

        directory = join(DIRECTORY, 'new', 'path')

        # Keep a handle on the real standard output
        stdout = sys.stdout
        sys.stdout = StringIO()
        script.push_directory(directory, final=True)

        # extract data
        sys.stdout.seek(0)
        output = sys.stdout.read().strip()

        # return stdout back to how it was
        sys.stdout = stdout
        assert output == '%s%s=%s' % (
            NZBGET_MSG_PREFIX,
            'FINALDIR',
            directory,
        )
        assert script.directory == directory
        assert script.system['DIRECTORY'] == directory

    def test_pushes(self):
        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)

        KEY = 'MY_VAR'
        VALUE = 'MY_VALUE'

        # Value doe snot exist yet
        assert script.get(KEY) is None

        # Keep a handle on the real standard output
        stdout = sys.stdout
        sys.stdout = StringIO()
        script.push(KEY, VALUE)

        # extract data
        sys.stdout.seek(0)
        output = sys.stdout.read().strip()

        # return stdout back to how it was
        sys.stdout = stdout
        assert output == '%s%s%s=%s' % (
            NZBGET_MSG_PREFIX,
            PUSH_ENVIRO_ID,
            KEY,
            VALUE,
        )
        assert script.get(KEY) == VALUE

    def test_validation(self):

        # This will fail because it's looking for the SCRIPTDIR
        # variable defined with NZBGet v11
        # a NZB Logger set to False uses stderr
        if '%sSCRIPTDIR' % SYS_ENVIRO_ID in os.environ:
            del os.environ['%sSCRIPTDIR' % SYS_ENVIRO_ID]
        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert not script.validate()
        del script

        # Now let's set it and try again
        os.environ['%sSCRIPTDIR' % SYS_ENVIRO_ID] = SCRIPTDIR
        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.validate()
        del os.environ['%sSCRIPTDIR' % SYS_ENVIRO_ID]
        del script

        # Now let's set it and try again
        os.environ['%sSCRIPTDIR' % SYS_ENVIRO_ID] = SCRIPTDIR
        os.environ['%sVALUE_A' % CFG_ENVIRO_ID] = 'A'
        os.environ['%sVALUE_B' % CFG_ENVIRO_ID] = 'B'
        os.environ['%sVALUE_C' % CFG_ENVIRO_ID] = 'C'

        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.validate(keys=(
            'Value_A', 'VALUE_B', 'value_c'
        ))
        del os.environ['%sSCRIPTDIR' % SYS_ENVIRO_ID]
        del os.environ['%sVALUE_A' % CFG_ENVIRO_ID]
        del os.environ['%sVALUE_B' % CFG_ENVIRO_ID]
        del os.environ['%sVALUE_C' % CFG_ENVIRO_ID]

    def test_health_check(self):
        """Test that wrapper for healthcheck is working correctly
        """
        # This will fail because it's looking for the SCRIPTDIR
        # variable defined with NZBGet v11
        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.health_check() is True
        assert script.health_check(
            is_unpacked=False, has_archive=False) is True

        assert script.health_check(is_unpacked=False) is True
        assert script.health_check(has_archive=True) is False

        script.version = 11
        assert script.health_check() is True
        assert script.health_check(
            is_unpacked=False, has_archive=False) is True

        assert script.health_check(is_unpacked=False) is True
        assert script.health_check(has_archive=True) is True
        del script

        os.environ['%sSTATUS' % POSTPROC_ENVIRO_ID] = '%s/%s' % (
            Health.FAILURE,
            Health.DEFAULT_SUB,
        )
        # NZBGet v11 support
        os.environ['%sPARSTATUS' % POSTPROC_ENVIRO_ID] = \
            str(PAR_STATUS.FAILURE)
        os.environ['%sUNPACKSTATUS' % POSTPROC_ENVIRO_ID] = \
            str(UNPACK_STATUS.FAILURE)

        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.health_check() is False
        assert script.health_check(
            is_unpacked=False, has_archive=False) is True

        assert script.health_check(is_unpacked=False) is True
        assert script.health_check(has_archive=True) is False

        script.version = 11
        assert script.health_check() is False
        assert script.health_check(
            is_unpacked=False, has_archive=False) is True

        assert script.health_check(is_unpacked=False) is True
        assert script.health_check(has_archive=True) is False

    def test_file_listings_as_string(self):

        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.get_files(search_dir=SEARCH_DIR) == {}

        # Create some temporary files to work with
        open(join(SEARCH_DIR, 'file.mkv'), 'w').close()
        open(join(SEARCH_DIR, 'file.par2'), 'w').close()
        open(join(SEARCH_DIR, 'file.PAR2'), 'w').close()
        open(join(SEARCH_DIR, 'file.txt'), 'w').close()
        open(join(SEARCH_DIR, 'sample.mp4'), 'w').close()
        open(join(SEARCH_DIR, 'sound.mp3'), 'w').close()

        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        files = script.get_files(search_dir=SEARCH_DIR)
        assert len(files) == 6
        index = [x for x in files.keys()][0]
        assert 'basename' in files[index]
        assert 'dirname' in files[index]
        assert 'extension' in files[index]
        assert 'filesize' not in files[index]
        assert 'modified' not in files[index]
        assert 'accessed' not in files[index]
        assert 'created' not in files[index]

        files = script.get_files(
            fullstats=True,
            search_dir=SEARCH_DIR,
        )
        assert len(files) == 6
        index = [x for x in files.keys()][0]
        assert 'basename' in files[index]
        assert 'dirname' in files[index]
        assert 'extension' in files[index]
        assert 'filesize' in files[index]
        assert 'modified' in files[index]
        assert 'accessed' in files[index]
        assert 'created' in files[index]

        # Test Filters (as strings)
        files = script.get_files(
            regex_filter='.*\.par2$',
            search_dir=SEARCH_DIR,
            case_sensitive=True,
        )
        assert len(files) == 1

        # Test Filters (as strings) (default is case-insensitive)
        files = script.get_files(
            regex_filter='.*\.par2$',
            search_dir=SEARCH_DIR,
        )
        assert len(files) == 2

        # Assume case sensitivity matters to us, we might
        # want to pre-compile our own list and pass it in
        files = script.get_files(
            regex_filter=re.compile('.*\.par2$', re.IGNORECASE),
            search_dir=SEARCH_DIR,
        )
        assert len(files) == 2

        # Test Filters (as strings)
        files = script.get_files(
            suffix_filter='.par2',
            search_dir=SEARCH_DIR,
        )
        assert len(files) == 1

        # Test Filters (as strings)
        # delimiters such as , (comma), / (slash), (space), etc
        # are automatically handled so you can chain them using
        # these
        files = script.get_files(
            suffix_filter='.par2,.PAR2',
            search_dir=SEARCH_DIR,
        )
        assert len(files) == 2

        # Test Filters (as strings)
        files = script.get_files(
            prefix_filter='sound',
            search_dir=SEARCH_DIR,
        )
        assert len(files) == 1

        # Test Filters (as strings)
        files = script.get_files(
            prefix_filter='sound, file',
            search_dir=SEARCH_DIR,
        )
        assert len(files) == 5

        # Test Filters (as strings)
        files = script.get_files(
            prefix_filter='s',
            search_dir=SEARCH_DIR,
        )
        assert len(files) == 2

    def test_file_listings_as_list(self):

        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.get_files(search_dir=[SEARCH_DIR, ]) == {}

        # Create some temporary files to work with
        open(join(SEARCH_DIR, 'file.mkv'), 'w').close()
        open(join(SEARCH_DIR, 'file.par2'), 'w').close()
        open(join(SEARCH_DIR, 'file.PAR2'), 'w').close()
        open(join(SEARCH_DIR, 'file.txt'), 'w').close()
        open(join(SEARCH_DIR, 'sample.mp4'), 'w').close()
        open(join(SEARCH_DIR, 'sound.mp3'), 'w').close()

        # Test Filters
        files = script.get_files(
            search_dir=[SEARCH_DIR, ],
            regex_filter=('.*\.par2$',),
            case_sensitive=True
        )
        assert len(files) == 1

        # Default is not case-sensitive
        files = script.get_files(
            search_dir=[SEARCH_DIR, ],
            regex_filter=('.*\.par2$',),
        )
        assert len(files) == 2

        # Assume case sensitivity matters to us, we might
        # want to pre-compile our own list and pass it in
        files = script.get_files(
            search_dir=[SEARCH_DIR, ],
            regex_filter=(re.compile('.*\.par2$', re.IGNORECASE),),
        )
        assert len(files) == 2

        # Test Filters (as strings)
        files = script.get_files(
            search_dir=[SEARCH_DIR, ],
            suffix_filter=('.par2',),
        )
        assert len(files) == 1

        # Test Filters (as strings)
        # delimiters such as , (comma), / (slash), (space), etc
        # are automatically handled so you can chain them using
        # these
        files = script.get_files(
            search_dir=[SEARCH_DIR, ],
            suffix_filter=('.par2,.PAR2',),
        )
        assert len(files) == 2

        files = script.get_files(
            search_dir=[SEARCH_DIR, ],
            suffix_filter=('.par2', '.PAR2'),
        )
        assert len(files) == 2

        files = script.get_files(
            search_dir=[SEARCH_DIR, ],
            prefix_filter=('sound',),
        )
        assert len(files) == 1

        files = script.get_files(
            search_dir=[SEARCH_DIR, ],
            prefix_filter=('sound, file',),
        )
        assert len(files) == 5

        # Duplicates should merge
        files = script.get_files(
            search_dir=[SEARCH_DIR, SEARCH_DIR, SEARCH_DIR],
            prefix_filter=('sound, file',),
        )
        assert len(files) == 5

    def test_nzbfilename_searching(self):

        # a NZB Logger set to False uses stderr
        script = PostProcessScript(
            logger=False,
            debug=VERY_VERBOSE_DEBUG,
            nzbfilename=NZBFILENAME_SHOW_A
        )
        assert script.parse_nzbfile(NZBFILENAME_SHOW_A)['LETTER'] == 'B'
        os.unlink(NZBFILENAME_SHOW_A)

        script = PostProcessScript(
            logger=False,
            debug=VERY_VERBOSE_DEBUG,
            nzbfilename=NZBFILENAME_SHOW_A
        )
        assert 'LETTER' not in script.parse_nzbfile(NZBFILENAME_SHOW_A)
        assert script.parse_nzbfile(
            NZBFILENAME_SHOW_A, check_queued=True)['LETTER'] == 'C'

        script = PostProcessScript(
            logger=False,
            debug=VERY_VERBOSE_DEBUG,
            nzbfilename=NZBFILENAME_SHOW_B
        )
        assert script.parse_nzbfile(NZBFILENAME_SHOW_B)['LETTER'] == 'D'

    def test_file_obsfucation(self):

        download_dir = join(TEMP_DIRECTORY, 'obsfucation')
        obsfucated_dir = join(download_dir, 'Afjk3af3D')

        # ensure directory doesn't exist
        try:
            rmtree(download_dir)
        except:
            pass
        try:
            rmtree(obsfucated_dir)
        except:
            pass
        makedirs(download_dir)
        makedirs(obsfucated_dir)

        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)

        assert len(script.parse_nzbfile(NZBFILENAME_SHOW_A)) == 5
        assert script.parse_nzbfile(NZBFILENAME_SHOW_A)['LETTER'] == 'B'
        assert script.parse_nzbfile(NZBFILENAME_SHOW_A)['PROPERNAME'] == \
            'A Great TV Show'
        assert script.parse_nzbfile(NZBFILENAME_SHOW_A)['NAME'] == \
            'A.Great.TV.Show.S04E06.720p.HDTV.x264-AWESOME'
        assert script.parse_nzbfile(NZBFILENAME_SHOW_A)['EPISODENAME'] == \
            'An Amazing Episode Name'
        assert script.parse_nzbfile(NZBFILENAME_SHOW_A)['CATEGORY'] == \
            'TV > HD'

        assert len(script.parse_nzbfile(NZBFILENAME)) == 5
        assert script.parse_nzbfile(NZBFILENAME)['LETTER'] == 'A'
        assert script.parse_nzbfile(NZBFILENAME)['CATEGORY'] == \
            'Movies > SD'
        assert script.parse_nzbfile(NZBFILENAME)['PROPERNAME'] == \
            'A Great Movie'
        assert script.parse_nzbfile(NZBFILENAME)['NAME'] == \
            'A.Great.Movie.1983.DVDRip.x264-AWESOME'
        assert script.parse_nzbfile(NZBFILENAME)['MOVIEYEAR'] == '1983'
        evil_filename = join(obsfucated_dir, 'ajklada3adaadfafdkl.mkv')
        good_filename = script.deobfuscate(
            filename=evil_filename,
        )
        assert basename(good_filename) == \
            'A.Great.Movie.1983.DVDRip.x264-AWESOME.mkv'

        # Same test, but if we didn't have the NZB-Name
        script.nzb_unset('name')
        good_filename = script.deobfuscate(
            filename=evil_filename,
        )
        assert basename(good_filename) == \
            'A.Great.Movie(1983).mkv'

        # If we don't have the ProperName, it gets even more scarse
        script.nzb_unset('propername')
        good_filename = script.deobfuscate(
            filename=evil_filename,
        )
        assert splitext(basename(good_filename))[0] == \
            splitext(basename(NZBFILENAME))[0]

        del script

        # cleanup
        try:
            rmtree(download_dir)
        except:
            pass
        try:
            rmtree(obsfucated_dir)
        except:
            pass

    def test_guesses(self):
        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=VERY_VERBOSE_DEBUG)

        guess_dict = {
            'type': 'movie',
            'title': 'A Great Title',
            'year': 1998,
            'screenSize': '720p',
            'format': 'HD-DVD',
            'audioCodec': 'DTS',
            'videoCodec': 'h264',
            'releaseGroup': 'GREATTEAM',
            'BadEntry': 'Ignored',
        }

        # Keep a handle on the real standard output
        stdout = sys.stdout
        sys.stdout = StringIO()
        script.push_guess(guess_dict)

        # extract data
        sys.stdout.seek(0)
        output = sys.stdout.read().strip()

        # return stdout back to how it was
        sys.stdout = stdout

        guess_keys = [x for x in guess_dict.keys()]
        guess_keys.remove('BadEntry')

        cmp_output = ['%s%s%s%s=%s' % (
            NZBGET_MSG_PREFIX,
            PUSH_ENVIRO_ID,
            SHR_ENVIRO_GUESS_ID,
            k.upper(),
            str(guess_dict[k]),
        ) for k in guess_keys]

        output = re.split('[\r\n]+', output)
        for _str in output:
            assert _str in cmp_output

        # Retrieve content
        results = script.pull_guess()

        # Minus 1 for BadEntry that should not
        # be part of fetch
        assert len(results) == len(guess_dict) - 1
        for k, v in results.items():
            assert k in guess_dict
            assert str(guess_dict[k]) == v
