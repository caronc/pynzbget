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
import re
from os.path import dirname
from os.path import join
from os import linesep
sys.path.insert(0, join(dirname(dirname(__file__)), 'nzbget'))

from ScriptBase import ScriptBase
from ScriptBase import SYS_ENVIRO_ID
from ScriptBase import EXIT_CODE
from ScriptBase import CFG_ENVIRO_ID
from ScriptBase import SHR_ENVIRO_ID
from ScriptBase import NZBGET_MSG_PREFIX
from ScriptBase import SHR_ENVIRO_GUESS_ID

from TestBase import TestBase
from TestBase import TEMP_DIRECTORY

from shutil import rmtree
from os import makedirs

import StringIO

SEARCH_DIR = join(TEMP_DIRECTORY, 'file_listing')

class TestScriptBase(TestBase):
    def setUp(self):
        # common
        super(TestScriptBase, self).setUp()

        # Create some environment variables
        os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sSCRIPTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY

        # ensure directory doesn't exist
        try:
            rmtree(SEARCH_DIR)
        except:
            pass
        makedirs(SEARCH_DIR)

    def tearDown(self):
        if '%sTEMPDIR' % SYS_ENVIRO_ID in os.environ:
            del os.environ['%sTEMPDIR' % SYS_ENVIRO_ID]
        if '%sSCRIPTDIR' % SYS_ENVIRO_ID in os.environ:
            del os.environ['%sSCRIPTDIR' % SYS_ENVIRO_ID]
        if '%sDEBUG' % CFG_ENVIRO_ID in os.environ:
            del os.environ['%sDEBUG' % CFG_ENVIRO_ID]

        try:
            rmtree(SEARCH_DIR)
        except:
            pass

        # common
        super(TestScriptBase, self).tearDown()

    def test_main_returns(self):

        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=True)
        assert script.run() == EXIT_CODE.SUCCESS

        del script
        del os.environ['%sSCRIPTDIR' % SYS_ENVIRO_ID]
        script = ScriptBase(logger=False, debug=True)
        assert script.run() == EXIT_CODE.FAILURE

        class ScriptExceptionExit(ScriptBase):
            def main(self, *args, **kwargs):
                raise TypeError

        script = ScriptExceptionExit()
        assert script.run() == EXIT_CODE.FAILURE

    def test_set_and_get(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=True)

        KEY = 'MY_VAR'
        VALUE = 'MY_VALUE'
        ADJUSTED_VALUE = 'MY_NEW_VALUE'

        # Value doe snot exist yet
        assert script.get(KEY) == None
        assert script.get(KEY, ADJUSTED_VALUE) == ADJUSTED_VALUE
        assert script.set(KEY, VALUE) == True
        assert script.get(KEY, ADJUSTED_VALUE) == VALUE

        # Remove a variable
        assert script.unset(KEY) == True
        # we'll get the default value now since the key wasn't
        # found.
        assert script.get(KEY, ADJUSTED_VALUE) == ADJUSTED_VALUE

        # Reset our value but be careful not to set the environment
        # or set the database
        assert script.set(KEY, VALUE, use_env=False, use_db=False) == True

        # observe content is not carried over
        script = ScriptBase(logger=False, debug=True, database_key='test')
        assert script.get(KEY) == None

        # The below line will include environment variables when
        # preforming the set and not the database
        assert script.set(KEY, VALUE, use_db=False) == True
        # If we destroy our instance
        del script

        # and reinitialize it; content should still carry from
        # the environment variable
        script = ScriptBase(logger=False, debug=True, database_key='test')
        assert script.get(KEY) == VALUE
        assert script.unset(KEY) == True

        # Now we set the database by just the database and not
        # the environment variable
        assert script.set(KEY, ADJUSTED_VALUE, use_env=False) == True

        # Destroy the instance
        del script
        script = ScriptBase(logger=False, debug=True, database_key='test')
        # We can still retrieve our adjusted value
        assert script.get(KEY) == ADJUSTED_VALUE
        # But not if we don't reference the database
        assert script.get(KEY, use_db=False) == None

        # if we don't set a database key, then there is no way for a
        # database connection to be established since we have no
        # container to work out of. This can be emulated by just creating
        # a ScriptBase object without a database_key set and we won't
        # connect to the database
        script = ScriptBase(logger=False, debug=True)

        # Now we set the database by just the database and not
        # the environment variable. Even though use_db defaults to
        # true, we won't write anythign to it since we can't establish
        # a connection to the database.

        # If we set a key...
        assert script.set(KEY, VALUE, use_env=False) == True

        # We can check that it was set
        assert script.get(KEY) == VALUE
        del script

        # But content won't carry over... infact, we'll fetch the last
        # key we fetched if we use the same database_key (allowing us
        # to access the same container as before)
        script = ScriptBase(logger=False, debug=True, database_key='test')
        # We can still retrieve our adjusted value
        assert script.get(KEY) == ADJUSTED_VALUE

        del script
        # But we won't get anything under a different container
        script = ScriptBase(logger=False, debug=True, database_key='ugh!')
        assert script.get(KEY) == None

    def test_file_listings_with_file(self):

        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=True)
        assert script.get_files(search_dir=[SEARCH_DIR, ]) == {}

        # Create some temporary files to work with
        open(join(SEARCH_DIR,'file.mkv'), 'w').close()
        open(join(SEARCH_DIR,'file.par2'), 'w').close()
        open(join(SEARCH_DIR,'file.PAR2'), 'w').close()
        open(join(SEARCH_DIR,'file.txt'), 'w').close()
        open(join(SEARCH_DIR,'sample.mp4'), 'w').close()
        open(join(SEARCH_DIR,'sound.mp3'), 'w').close()

        # Search File
        files = script.get_files(
            search_dir=join(SEARCH_DIR, 'file.mkv'),
        )
        assert len(files) == 1

        files = script.get_files(
            search_dir=join(SEARCH_DIR, 'file.mkv'),
            suffix_filter='.mov',
        )
        assert len(files) == 0

        files = script.get_files(
            search_dir=join(SEARCH_DIR, 'file.mkv'),
            suffix_filter='.mkv',
        )
        assert len(files) == 1


        files = script.get_files(
            search_dir=join(SEARCH_DIR, 'file.mkv'),
            suffix_filter='.mkv',
            prefix_filter='fi',
        )
        assert len(files) == 1

        files = script.get_files(
            search_dir=join(SEARCH_DIR, 'file.mkv'),
            suffix_filter='.mkv',
            prefix_filter='file',
        )
        assert len(files) == 1

        # Absolute match
        files = script.get_files(
            search_dir=join(SEARCH_DIR, 'file.mkv'),
            suffix_filter='file.mkv',
            prefix_filter='file.mkv',
        )
        assert len(files) == 1

        files = script.get_files(
            search_dir=join(SEARCH_DIR, 'file.mkv'),
            regex_filter='^file\.mkv$',
        )
        assert len(files) == 1

        files = script.get_files(
            search_dir=join(SEARCH_DIR, 'file.mkv'),
            suffix_filter='file.mkv',
            prefix_filter='file.mkv',
            regex_filter='^file\.mkv$',
        )
        assert len(files) == 1

    def test_parse_list(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=True)

        # A simple single array entry (As str)
        results = script.parse_list('.mkv,.avi,.divx,.xvid,' + \
                '.mov,.wmv,.mp4,.mpg,.mpeg,.vob,.iso')
        assert results == [
            '.divx', '.iso', '.mkv', '.mov', '.mpg',
            '.avi', '.mpeg', '.vob', '.xvid', '.wmv', '.mp4',
        ]

        # Now 2 lists with lots of duplicates and other delimiters
        results = script.parse_list('.mkv,.avi,.divx,.xvid,' + \
                '.mov,.wmv,.mp4,.mpg:.mpeg,.vob,,/',
                '.mkv,.avi,.divx,.xvid,' + \
                '.mov        :.wmv,.mp4//.mpg,.mpeg,.vob,.iso')
        assert results == [
            '.divx', '.iso', '.mkv', '.mov', '.mpg',
            '.avi', '.mpeg', '.vob', '.xvid', '.wmv', '.mp4',
        ]

        # Now a list with extras we want to add as strings
        # empty entries are removed
        results = script.parse_list([
            '.divx', '.iso', '.mkv', '.mov','', '  ',
            '.avi', '.mpeg', '.vob', '.xvid', '.mp4',
        ],
            '.mov,.wmv,.mp4,.mpg',
        )
        assert results == [
            '.divx', '.wmv', '.iso', '.mkv', '.mov',
            '.mpg', '.avi', '.vob', '.xvid', '.mpeg', '.mp4',
        ]

    def test_parse_path_list01(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=True)

        # A simple single array entry (As str)
        results = script.parse_path_list(
            'C:\\test path with space\\and more spaces\\',
            'D:\\weird path\\more spaces\\ ',
            'D:\\weird path\\more spaces\\ G:\\save E:\\\\save_dir',
            'D:\\weird path\\more spaces\\ ', # Duplicate is removed
            '  D:\\\\weird path\\more spaces\\\\ ', # Duplicate is removed
            'relative path\\\\\\with\\crap\\\\ second_path\\more spaces\\ ',
            # Windows Network Paths
            '\\\\a\\network\\path\\\\ \\\\\\another\\nw\\\\path\\\\         ',
            # lists supported too
            [ 'relative path\\in\\list', 'second_path\\more spaces\\\\' ],
            # Unsupported and ignored types
            None, 1, 4.3, True, False, -4000,
        )

        assert len(results) == 9
        assert 'D:\\weird path\\more spaces' in results
        assert 'E:\\save_dir' in results
        assert 'G:\\save' in results
        assert 'second_path\\more spaces' in results
        assert '\\\\a\\network\\path' in results
        assert '\\\\another\\nw\\path' in results
        assert 'relative path\\with\\crap' in results
        assert 'relative path\\in\\list' in results
        assert 'C:\\test path with space\\and more spaces' in results

    def test_parse_path_list02(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=True)

        # A simple single array entry (As str)
        results = script.parse_path_list(
            # 3 paths identified below
            '//absolute/path /another///absolute//path/// /',
            # A whole slew of duplicates and list inside list
            '/', [ '/', '/', '//', '//////', [ '/', '' ], ],
            'relative/path/here',
            'relative/path/here/',
            'another/relative////path///',
        )
        assert len(results) == 5
        assert '/absolute/path' in results
        assert 'another/absolute/path' in results
        assert 'another/absolute/path' in results
        assert '/' in results
        assert 'relative/path/here' in results

    def test_parse_bool(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=True)
        assert script.parse_bool('Yes') == True
        assert script.parse_bool('YES') == True
        assert script.parse_bool('No') == False
        assert script.parse_bool('NO') == False
        assert script.parse_bool('TrUE') == True
        assert script.parse_bool('tRUe') == True
        assert script.parse_bool('FAlse') == False
        assert script.parse_bool('F') == False
        assert script.parse_bool('T') == True
        assert script.parse_bool('0') == False
        assert script.parse_bool('1') == True
        assert script.parse_bool('True') == True
        assert script.parse_bool('Yes') == True
        assert script.parse_bool(1) == True
        assert script.parse_bool(0) == False
        assert script.parse_bool(True) == True
        assert script.parse_bool(False) == False

        # only the int of 0 will return False since the function
        # casts this to a boolean
        assert script.parse_bool(2) == True
        # An empty list is still false
        assert script.parse_bool([]) == False
        # But a list that contains something is True
        assert script.parse_bool(['value',]) == True

        # Use Default (which is False)
        assert script.parse_bool('OhYeah') == False
        # Adjust Default and get a different result
        assert script.parse_bool('OhYeah', True) == True

    def test_guesses(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=True)

        guess_dict = {
            'type': 'movie',
            'title':'A Great Title',
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
        sys.stdout = StringIO.StringIO()
        script.push_guess(guess_dict)

        # extract data
        sys.stdout.seek(0)
        output = sys.stdout.read().strip()

        # return stdout back to how it was
        sys.stdout = stdout

        guess_keys = guess_dict.keys()
        guess_keys.remove('BadEntry')
        cmp_output = ['%s%s%s%s=%s' % (
            NZBGET_MSG_PREFIX,
            SHR_ENVIRO_ID,
            SHR_ENVIRO_GUESS_ID,
            k.upper(),
            str(guess_dict[k]),
        ) for k in guess_keys ]

        output = re.split('[\r\n]+', output)
        # Clean "" entry
        output = filter(bool, output)

        # Pushes are disabled in Standalone mode
        assert len(output) == 0

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

        sys.stdout = stdout

        # Pushes are disabled in Standalone mode
        output = re.split('[\r\n]+', output)
        # Clean "" entry
        output = filter(bool, output)

        assert len(output) == 0
        assert script.get(KEY) == VALUE
