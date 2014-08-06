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

import StringIO

class TestScriptBase(TestBase):
    def setUp(self):
        # common
        super(TestScriptBase, self).setUp()

        # Create some environment variables
        os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sSCRIPTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY

    def tearDown(self):
        if '%sTEMPDIR' % SYS_ENVIRO_ID in os.environ:
            del os.environ['%sTEMPDIR' % SYS_ENVIRO_ID]
        if '%sSCRIPTDIR' % SYS_ENVIRO_ID in os.environ:
            del os.environ['%sSCRIPTDIR' % SYS_ENVIRO_ID]
        if '%sDEBUG' % CFG_ENVIRO_ID in os.environ:
            del os.environ['%sDEBUG' % CFG_ENVIRO_ID]

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

        # return stdout back to how it was
        sys.stdout = stdout
        assert output == '%s%s%s=%s' % (
            NZBGET_MSG_PREFIX,
            SHR_ENVIRO_ID,
            KEY,
            VALUE,
        )
        assert script.get(KEY) == VALUE

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

        guess_keys = sorted(guess_dict.keys())
        guess_keys.remove('BadEntry')
        cmp_output = ['%s%s%s%s=%s' % (
            NZBGET_MSG_PREFIX,
            SHR_ENVIRO_ID,
            SHR_ENVIRO_GUESS_ID,
            k.upper(),
            str(guess_dict[k]),
        ) for k in sorted(guess_keys) ]

        assert output == linesep.join(cmp_output)

        # Retrieve content
        results = script.pull_guess()

        # Minus 1 for BadEntry that should not
        # be part of fetch
        assert len(results) == len(guess_dict) - 1
        for k, v in results.items():
            assert k in guess_dict
            assert str(guess_dict[k]) == v