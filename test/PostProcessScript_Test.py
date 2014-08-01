# -*- encoding: utf-8 -*-
#
# A Test Suite (for nose) for the PostProcessScript Class
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
import re
from os import makedirs
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext
sys.path.insert(0, join(dirname(dirname(__file__)), 'nzbget'))

from ScriptBase import CFG_ENVIRO_ID
from ScriptBase import SYS_ENVIRO_ID
from ScriptBase import SHR_ENVIRO_ID
from ScriptBase import NZBGET_MSG_PREFIX

from PostProcessScript import PostProcessScript
from PostProcessScript import POSTPROC_ENVIRO_ID
from PostProcessScript import SCRIPT_STATUS
from PostProcessScript import TOTAL_STATUS
from PostProcessScript import PAR_STATUS
from PostProcessScript import UNPACK_STATUS

from TestBase import TestBase
from TestBase import TEMP_DIRECTORY

import StringIO

from shutil import rmtree

# Some constants to work with
DIRECTORY = TEMP_DIRECTORY
NZBNAME = 'A.Great.Movie'
NZBFILENAME = join(TEMP_DIRECTORY, 'A.Great.Movie.nzb')
NZBFILENAME_SHOW = join(TEMP_DIRECTORY, 'A.Great.TV.Show.nzb')
CATEGORY = 'movie'
TOTALSTATUS = TOTAL_STATUS.SUCCESS
STATUS = SCRIPT_STATUS.SUCCESS
SCRIPTSTATUS = 'SUCCESS/ALL'
PARSTATUS = PAR_STATUS.SUCCESS
UNPACKSTATUS = UNPACK_STATUS.SUCCESS

# For validation
SCRIPTDIR = join(TEMP_DIRECTORY, 'scripts')

class TestPostProcessScript(TestBase):
    def setUp(self):
        # common
        super(TestPostProcessScript, self).setUp()

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
            </head>
          </nzb>""")
        _f.close()

        _f = open(NZBFILENAME_SHOW, 'w')
        _f.write("""<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE nzb PUBLIC "-//newzBin//DTD NZB 1.1//EN" "http://www.newzbin.com/DTD/nzb/nzb-1.1.dtd">
            <nzb xmlns="http://www.newzbin.com/DTD/2003/nzb">

            <head>
             <meta type="category">TV &gt; HD</meta>
             <meta type="name">A.Great.TV.Show.S04E06.720p.HDTV.x264-AWESOME</meta>
             <meta type="propername">A Great TV Show</meta>
             <meta type="episodename">An Amazing Episode Name</meta>
            </head>
          </nzb>""")
        _f.close()

        # Create some environment variables
        os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
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

    def tearDown(self):
        # Eliminate any variables defined
        del os.environ['%sTEMPDIR' % SYS_ENVIRO_ID]
        del os.environ['%sDIRECTORY' % POSTPROC_ENVIRO_ID]
        del os.environ['%sNZBNAME' % POSTPROC_ENVIRO_ID]
        del os.environ['%sNZBFILENAME' % POSTPROC_ENVIRO_ID]
        del os.environ['%sCATEGORY' % POSTPROC_ENVIRO_ID]
        del os.environ['%sTOTALSTATUS' % POSTPROC_ENVIRO_ID]
        del os.environ['%sSCRIPTSTATUS' % POSTPROC_ENVIRO_ID]
        del os.environ['%sPARSTATUS' % POSTPROC_ENVIRO_ID]
        del os.environ['%sUNPACKSTATUS' % POSTPROC_ENVIRO_ID]

        # common
        super(TestPostProcessScript, self).tearDown()

    def test_environment_varable_init(self):
        """
        Testing NZBGet Script initialization using environment variables
        """
        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=True)
        assert script.directory == DIRECTORY
        assert script.nzbname == NZBNAME
        assert script.nzbfilename == NZBFILENAME
        assert script.category == CATEGORY
        assert script.totalstatus == TOTALSTATUS
        assert script.status == STATUS
        assert script.scriptstatus == SCRIPTSTATUS
        assert script.parstatus == PARSTATUS
        assert script.unpackstatus == UNPACKSTATUS

        assert script.system['TEMPDIR'] == TEMP_DIRECTORY
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
        assert script.get('DIRECTORY') == DIRECTORY
        assert script.get('NZBNAME') == NZBNAME
        assert script.get('NZBFILENAME') == NZBFILENAME
        assert script.get('CATEGORY') == CATEGORY
        assert script.get('TOTALSTATUS') == TOTALSTATUS
        assert script.get('STATUS') == STATUS
        assert script.get('SCRIPTSTATUS') == SCRIPTSTATUS
        assert script.get('PARSTATUS') == PARSTATUS
        assert script.get('UNPACKSTATUS') == UNPACKSTATUS

        assert script.config == {}

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
        status = SCRIPT_STATUS.FAILURE
        scriptstatus = 'FAILURE/UNPACK'
        parstatus = PAR_STATUS.FAILURE
        unpackstatus = UNPACK_STATUS.FAILURE

        script = PostProcessScript(
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
           # a NZB Logger set to False uses stderr
           logger=False,
           debug=True,
        )

        assert script.directory == directory
        assert script.nzbname == nzbname
        assert script.nzbfilename == nzbfilename
        assert script.category == category
        assert script.totalstatus == totalstatus
        assert script.status == status
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

        assert script.config == {}

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
        script = PostProcessScript(logger=False, debug=True)

        KEY = 'MY_VAR'
        VALUE = 'MY_VALUE'

        # Value doe snot exist yet
        assert script.get(KEY) == None
        assert script.get(KEY, 'Default') == 'Default'
        assert script.set(KEY, VALUE) == True
        assert script.get(KEY, 'Default') == VALUE


    def test_config_varable_init(self):
        valid_entries = {
            'MY_CONFIG_ENTRY' : 'Option A',
            'ENTRY_WITH_234_NUMBERS' : 'Option B',
            '123443' : 'Option C',
        }
        invalid_entries = {
            'CONFIG_ENtry_skipped' : 'Option',
            'CONFIG_ENtry_$#': 'Option',
            # Empty
            '': 'Option',
        }
        for k, v in valid_entries.items():
            os.environ['%s%s' % (CFG_ENVIRO_ID, k)] = v
        for k, v in invalid_entries.items():
            os.environ['%s%s' % (CFG_ENVIRO_ID, k)] = v

        script = PostProcessScript()
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
        script = PostProcessScript(logger=False, debug=True)

        directory = join(DIRECTORY, 'new', 'path')

        # Keep a handle on the real standard output
        stdout = sys.stdout
        sys.stdout = StringIO.StringIO()
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
        script = PostProcessScript(logger=False, debug=True)

        directory = join(DIRECTORY, 'new', 'path')

        # Keep a handle on the real standard output
        stdout = sys.stdout
        sys.stdout = StringIO.StringIO()
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

    def test_validation(self):

        # This will fail because it's looking for the SCRIPTDIR
        # variable defined with NZBGet v11
        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=True)
        assert not script.validate()
        del script

        # Now let's set it and try again
        os.environ['%sSCRIPTDIR' % CFG_ENVIRO_ID] = SCRIPTDIR
        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=True)
        assert script.validate()
        del os.environ['%sSCRIPTDIR' % CFG_ENVIRO_ID]
        del script

    def test_file_listings_as_string(self):

        search_dir = join(TEMP_DIRECTORY, 'file_listing')
        # ensure directory doesn't exist
        try:
            rmtree(search_dir)
        except:
            pass
        makedirs(search_dir)

        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=True)
        assert script.get_files(search_dir=search_dir) == {}

        # Create some temporary files to work with
        open(join(search_dir,'file.mkv'), 'w').close()
        open(join(search_dir,'file.par2'), 'w').close()
        open(join(search_dir,'file.PAR2'), 'w').close()
        open(join(search_dir,'file.txt'), 'w').close()
        open(join(search_dir,'sample.mp4'), 'w').close()
        open(join(search_dir,'sound.mp3'), 'w').close()

        script = PostProcessScript(logger=False, debug=True)
        files = script.get_files(search_dir=search_dir)
        assert len(files) == 6
        assert 'basename' in files[files.keys()[0]]
        assert 'dirname' in files[files.keys()[0]]
        assert 'extension' in files[files.keys()[0]]
        assert 'filesize' not in files[files.keys()[0]]
        assert 'modified' not in files[files.keys()[0]]

        files = script.get_files(
            fullstats=True,
            search_dir=search_dir,
        )
        assert len(files) == 6
        assert 'basename' in files[files.keys()[0]]
        assert 'dirname' in files[files.keys()[0]]
        assert 'extension' in files[files.keys()[0]]
        assert 'filesize' in files[files.keys()[0]]
        assert 'modified' in files[files.keys()[0]]

        # Test Filters (as strings)
        files = script.get_files(
            regex_filter='.*\.par2$',
            search_dir=search_dir,
        )
        assert len(files) == 1

        # Assume case sensitivity matters to us, we might
        # want to pre-compile our own list and pass it in
        files = script.get_files(
            regex_filter=re.compile('.*\.par2$', re.IGNORECASE),
            search_dir=search_dir,
        )
        assert len(files) == 2

        # Test Filters (as strings)
        files = script.get_files(
            suffix_filter='.par2',
            search_dir=search_dir,
        )
        assert len(files) == 1

        # Test Filters (as strings)
        # delimiters such as , (comma), / (slash), (space), etc
        # are automatically handled so you can chain them using
        # these
        files = script.get_files(
            suffix_filter='.par2,.PAR2',
            search_dir=search_dir,
        )
        assert len(files) == 2

        # Test Filters (as strings)
        files = script.get_files(
            prefix_filter='sound',
            search_dir=search_dir,
        )
        assert len(files) == 1

        # Test Filters (as strings)
        files = script.get_files(
            prefix_filter='sound, file',
            search_dir=search_dir,
        )
        assert len(files) == 5

        # Test Filters (as strings)
        files = script.get_files(
            prefix_filter='s',
            search_dir=search_dir,
        )
        assert len(files) == 2

        # cleanup
        try:
            rmtree(search_dir)
        except:
            pass

    def test_file_listings_as_list(self):

        search_dir = join(TEMP_DIRECTORY, 'file_listing')
        # ensure directory doesn't exist
        try:
            rmtree(search_dir)
        except:
            pass
        makedirs(search_dir)

        # a NZB Logger set to False uses stderr
        script = PostProcessScript(logger=False, debug=True)
        assert script.get_files(search_dir=search_dir) == {}

        # Create some temporary files to work with
        open(join(search_dir,'file.mkv'), 'w').close()
        open(join(search_dir,'file.par2'), 'w').close()
        open(join(search_dir,'file.PAR2'), 'w').close()
        open(join(search_dir,'file.txt'), 'w').close()
        open(join(search_dir,'sample.mp4'), 'w').close()
        open(join(search_dir,'sound.mp3'), 'w').close()

        # Test Filters
        files = script.get_files(
            regex_filter=('.*\.par2$',),
            search_dir=search_dir,
        )
        assert len(files) == 1

        # Assume case sensitivity matters to us, we might
        # want to pre-compile our own list and pass it in
        files = script.get_files(
            regex_filter=(re.compile('.*\.par2$', re.IGNORECASE),),
            search_dir=search_dir,
        )
        assert len(files) == 2

        # Test Filters (as strings)
        files = script.get_files(
            suffix_filter=('.par2',),
            search_dir=search_dir,
        )
        assert len(files) == 1

        # Test Filters (as strings)
        # delimiters such as , (comma), / (slash), (space), etc
        # are automatically handled so you can chain them using
        # these
        files = script.get_files(
            suffix_filter=('.par2,.PAR2',),
            search_dir=search_dir,
        )
        assert len(files) == 2

        files = script.get_files(
            suffix_filter=('.par2','.PAR2'),
            search_dir=search_dir,
        )
        assert len(files) == 2

        # Test Filters (as strings)
        files = script.get_files(
            prefix_filter=('sound',),
            search_dir=search_dir,
        )
        assert len(files) == 1

        # Test Filters (as strings)
        files = script.get_files(
            prefix_filter=('sound, file',),
            search_dir=search_dir,
        )
        assert len(files) == 5

        # cleanup
        try:
            rmtree(search_dir)
        except:
            pass

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
        script = PostProcessScript(logger=False, debug=True)
        assert len(script.parse_nzbfile(NZBFILENAME_SHOW)) == 4
        assert script.parse_nzbfile(NZBFILENAME_SHOW)['PROPERNAME'] == \
                'A Great TV Show'
        assert script.parse_nzbfile(NZBFILENAME_SHOW)['NAME'] == \
                'A.Great.TV.Show.S04E06.720p.HDTV.x264-AWESOME'
        assert script.parse_nzbfile(NZBFILENAME_SHOW)['EPISODENAME'] == \
                'An Amazing Episode Name'
        assert script.parse_nzbfile(NZBFILENAME_SHOW)['CATEGORY'] == 'TV > HD'

        assert len(script.parse_nzbfile(NZBFILENAME)) == 4
        assert script.parse_nzbfile(NZBFILENAME)['CATEGORY'] == 'Movies > SD'
        assert script.parse_nzbfile(NZBFILENAME)['PROPERNAME'] == \
                'A Great Movie'
        assert script.parse_nzbfile(NZBFILENAME)['NAME'] == \
                'A.Great.Movie.1983.DVDRip.x264-AWESOME'
        assert script.parse_nzbfile(NZBFILENAME)['MOVIEYEAR'] == '1983'
        evil_filename = join(obsfucated_dir, 'ajklada3adaadfafdkl.mkv')
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
