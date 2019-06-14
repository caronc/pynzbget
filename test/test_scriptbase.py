# -*- encoding: utf-8 -*-
#
# A Test Suite (for nose) for the ScriptBase Class
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
from os.path import join
from os.path import isfile
try:
    # Python 2.7
    from urllib import unquote

except ImportError:
    # Python 3.x
    from urllib.parse import unquote

from TestBase import TestBase
from TestBase import TEMP_DIRECTORY

from nzbget.ScriptBase import ScriptBase
from nzbget.ScriptBase import SYS_ENVIRO_ID
from nzbget.ScriptBase import SHELL_EXIT_CODE
from nzbget.ScriptBase import CFG_ENVIRO_ID
from nzbget.ScriptBase import Health
from nzbget.Logger import VERY_VERBOSE_DEBUG

from shutil import rmtree
from os import makedirs
from threading import Thread, Lock
from time import sleep

try:
    # Python v2.7
    from StringIO import StringIO
except ImportError:
    # Python v3.x
    from io import StringIO

SEARCH_DIR = join(TEMP_DIRECTORY, 'file_listing')


class TestScriptBase(TestBase):
    def setup_method(self):
        # common
        super(TestScriptBase, self).setup_method()

        # Create some environment variables
        os.environ['%sTEMPDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY
        os.environ['%sSCRIPTDIR' % SYS_ENVIRO_ID] = TEMP_DIRECTORY

        # ensure directory doesn't exist
        try:
            rmtree(SEARCH_DIR)
        except:
            pass
        makedirs(SEARCH_DIR)

    def teardown_method(self):
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
        super(TestScriptBase, self).teardown_method()

    def test_main_returns(self):

        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.run() == SHELL_EXIT_CODE.SUCCESS

        class ScriptExceptionExit(ScriptBase):
            def main(self, *args, **kwargs):
                raise TypeError

        script = ScriptExceptionExit()
        assert script.run() == SHELL_EXIT_CODE.FAILURE

    def test_nzbset_and_nzbget(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)
        KEY = 'MY_NZBVAR'
        KEYL = 'my_nzbvar'
        VALUE = 'MY_NZBVALUE'
        ADJUSTED_VALUE = 'MY_NEW_NZBVALUE'

        # Value does not exist yet
        assert script.nzb_get(KEY) is None
        assert script.nzb_get(KEY, ADJUSTED_VALUE) == ADJUSTED_VALUE
        assert script.nzb_get(KEYL, ADJUSTED_VALUE) == ADJUSTED_VALUE
        assert script.nzb_set(KEY, VALUE) is True
        assert script.nzb_get(KEY, ADJUSTED_VALUE) == VALUE
        assert script.nzb_get(KEYL, ADJUSTED_VALUE) == VALUE
        assert script.nzb_unset(KEYL) is True
        assert script.nzb_get(KEY, ADJUSTED_VALUE) == ADJUSTED_VALUE

        # Reset with content
        assert script.nzb_set(KEY, ADJUSTED_VALUE) is True
        assert script.nzb_get(KEY, VALUE) == ADJUSTED_VALUE

        # Same as nzb_unset
        assert script.nzb_set(KEY, None) is True
        assert script.nzb_get(KEY, VALUE) == VALUE

    def test_set_and_get(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)

        KEY = 'MY_VAR_TEST123'
        VALUE = 'MY_VALUE'
        ADJUSTED_VALUE = 'MY_NEW_VALUE'

        # Value does not exist yet
        assert script.get(KEY) is None
        assert script.get(KEY, ADJUSTED_VALUE) == ADJUSTED_VALUE
        assert script.set(KEY, VALUE) is True
        assert script.get(KEY, ADJUSTED_VALUE) == VALUE

        # Remove a variable
        assert script.unset(KEY) is True
        # we'll get the default value now since the key wasn't
        # found.
        assert script.get(KEY, ADJUSTED_VALUE) == ADJUSTED_VALUE

        # Reset our value but be careful not to set the environment
        # or set the database
        assert script.set(KEY, VALUE, use_env=False, use_db=False) is True

        # observe content is not carried over
        script = ScriptBase(
            logger=False, debug=VERY_VERBOSE_DEBUG, database_key='test')
        assert script.get(KEY) is None

        # The below line will include environment variables when
        # preforming the set and not the database
        assert script.set(KEY, VALUE, use_db=False) is True
        # If we destroy our instance
        del script

        # and reinitialize it; content should still carry from
        # the environment variable
        script = ScriptBase(
            logger=False, debug=VERY_VERBOSE_DEBUG, database_key='test')
        assert script.get(KEY) == VALUE
        assert script.unset(KEY) is True

        # Now we set the database by just the database and not
        # the environment variable
        assert script.set(KEY, ADJUSTED_VALUE, use_env=False) is True

        # Destroy the instance
        del script
        script = ScriptBase(
            logger=False, debug=VERY_VERBOSE_DEBUG, database_key='test')
        # We can still retrieve our adjusted value
        assert script.get(KEY) == ADJUSTED_VALUE
        # But not if we don't reference the database
        assert script.get(KEY, use_db=False) is None

        # if we don't set a database key, then there is no way for a
        # database connection to be established since we have no
        # container to work out of. This can be emulated by just creating
        # a ScriptBase object without a database_key set and we won't
        # connect to the database
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)

        # Now we set the database by just the database and not
        # the environment variable. Even though use_db defaults to
        # true, we won't write anythign to it since we can't establish
        # a connection to the database.

        # If we set a key...
        assert script.set(KEY, VALUE, use_env=False) is True

        # We can check that it was set
        assert script.get(KEY) == VALUE
        del script

        # But content won't carry over... infact, we'll fetch the last
        # key we fetched if we use the same database_key (allowing us
        # to access the same container as before)
        script = ScriptBase(
            logger=False, debug=VERY_VERBOSE_DEBUG, database_key='test')
        # We can still retrieve our adjusted value
        assert script.get(KEY) == ADJUSTED_VALUE

        del script
        # But we won't get anything under a different container
        script = ScriptBase(
            logger=False, debug=VERY_VERBOSE_DEBUG, database_key='ugh!')
        assert script.get(KEY) is None

    def test_file_listings_with_file(self):

        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.get_files(search_dir=[SEARCH_DIR, ]) == {}

        # Create some temporary files to work with
        open(join(SEARCH_DIR, 'file.mkv'), 'w').close()
        open(join(SEARCH_DIR, 'file.par2'), 'w').close()
        open(join(SEARCH_DIR, 'file.PAR2'), 'w').close()
        open(join(SEARCH_DIR, 'file.txt'), 'w').close()
        open(join(SEARCH_DIR, 'sample.mp4'), 'w').close()
        open(join(SEARCH_DIR, 'sound.mp3'), 'w').close()
        open(join(SEARCH_DIR, 'NOEXTENSION'), 'w').close()

        files = script.get_files(
            search_dir=SEARCH_DIR,
        )
        assert len(files) == 7

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
            regex_filter=r'^file\.mkv$',
        )
        assert len(files) == 1

        files = script.get_files(
            search_dir=join(SEARCH_DIR, 'file.mkv'),
            suffix_filter='file.mkv',
            prefix_filter='file.mkv',
            regex_filter=r'^file\.mkv$',
        )
        assert len(files) == 1

    def test_file_listings_with_depth(self):

        subdirs = (
            'depth2/depth3/depth4/depth5',
            'depth2_a/depth3_a/depth4_a/depth5_a',
            'depth2_b/depth3_b/depth4_b/depth5_b',
            'depth2_c/depth3_c/depth4_c/depth5_c/depth6_c',
        )
        for _dir in subdirs:
            makedirs(join(SEARCH_DIR, _dir))

        # Create some temporary files to work with
        open(join(SEARCH_DIR, 'file.001'), 'w').close()
        open(join(SEARCH_DIR, 'depth2_c', 'depth3_c',
                  'depth4_c', 'depth5_c', 'depth6_c', 'file.006'), 'w').close()
        open(join(SEARCH_DIR, 'depth2', 'depth3', 'depth4',
                  'depth5', 'file.005'), 'w').close()
        open(join(SEARCH_DIR, 'depth2_a', 'depth3_a', 'depth4_a',
                  'depth5_a', 'file.005'), 'w').close()
        open(join(SEARCH_DIR, 'depth2_b', 'depth3_b', 'depth4_b',
                  'depth5_b', 'file.005'), 'w').close()
        open(join(SEARCH_DIR, 'depth2', 'depth3', 'depth4',
                  'file.004'), 'w').close()
        open(join(SEARCH_DIR, 'depth2', 'depth3',
                  'file.003'), 'w').close()
        open(join(SEARCH_DIR, 'depth2', 'file.002'), 'w').close()

        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)
        results = script.get_files(search_dir=SEARCH_DIR, max_depth=2)
        assert len(results) == 2
        assert join(SEARCH_DIR, 'depth2', 'file.002') in results.keys()
        assert join(SEARCH_DIR, 'file.001') in results.keys()

        # Recursion works a little differnetly, check that results
        # are the same:
        results = script.get_files(search_dir=[SEARCH_DIR, ], max_depth=2)
        assert len(results) == 2
        assert join(SEARCH_DIR, 'depth2', 'file.002') in results.keys()
        assert join(SEARCH_DIR, 'file.001') in results.keys()

        # This should fetch them all
        files = script.get_files(SEARCH_DIR)
        assert len(files) == 8

        # A list of directories should scan the same content, minus stuff at
        # the root
        files = script.get_files(
            [join(SEARCH_DIR, re.split('/', _dir)[0]) for _dir in subdirs])
        assert len(files) == 7

    def test_file_listings_ignored_directories(self):
        from nzbget.ScriptBase import SKIP_DIRECTORIES

        # Create some bad directories
        for _dir in SKIP_DIRECTORIES:
            makedirs(join(SEARCH_DIR, _dir))
            open(join(SEARCH_DIR, _dir, 'ignore_me.mkv'), 'w').close()

        # Create some temporary files to work with
        makedirs(join(SEARCH_DIR, 'good_dir'))
        open(join(SEARCH_DIR, 'good_file1.mkv'), 'w').close()
        open(join(SEARCH_DIR, 'good_file2.mkv'), 'w').close()
        open(join(SEARCH_DIR, 'good_dir', 'good_file3.mkv'), 'w').close()

        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)
        results = script.get_files(search_dir=SEARCH_DIR)
        assert len(results) == 3
        assert join(SEARCH_DIR, 'good_file1.mkv') in results.keys()
        assert join(SEARCH_DIR, 'good_file2.mkv') in results.keys()
        assert join(SEARCH_DIR, 'good_dir', 'good_file3.mkv') in \
            results.keys()

    def test_parse_url01(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)

        result = script.parse_url('http://hostname')
        assert result['schema'] == 'http'
        assert result['host'] == 'hostname'
        assert result['port'] is None
        assert result['user'] is None
        assert result['password'] is None
        assert result['fullpath'] is None
        assert result['path'] is None
        assert result['query'] is None
        assert result['url'] == 'http://hostname'
        assert result['qsd'] == {}

        result = script.parse_url('http://hostname/')
        assert result['schema'] == 'http'
        assert result['host'] == 'hostname'
        assert result['port'] is None
        assert result['user'] is None
        assert result['password'] is None
        assert result['fullpath'] == '/'
        assert result['path'] == '/'
        assert result['query'] is None
        assert result['url'] == 'http://hostname/'
        assert result['qsd'] == {}

        result = script.parse_url('hostname')
        assert result['schema'] == 'http'
        assert result['host'] == 'hostname'
        assert result['port'] is None
        assert result['user'] is None
        assert result['password'] is None
        assert result['fullpath'] is None
        assert result['path'] is None
        assert result['query'] is None
        assert result['url'] == 'http://hostname'
        assert result['qsd'] == {}

        result = script.parse_url('http://hostname////')
        assert result['schema'] == 'http'
        assert result['host'] == 'hostname'
        assert result['port'] is None
        assert result['user'] is None
        assert result['password'] is None
        assert result['fullpath'] == '/'
        assert result['path'] == '/'
        assert result['query'] is None
        assert result['url'] == 'http://hostname/'
        assert result['qsd'] == {}

        result = script.parse_url('http://hostname:40////')
        assert result['schema'] == 'http'
        assert result['host'] == 'hostname'
        assert result['port'] == 40
        assert result['user'] is None
        assert result['password'] is None
        assert result['fullpath'] == '/'
        assert result['path'] == '/'
        assert result['query'] is None
        assert result['url'] == 'http://hostname:40/'
        assert result['qsd'] == {}

        result = script.parse_url('HTTP://HoStNaMe:40/test.php')
        assert result['schema'] == 'http'
        assert result['host'] == 'HoStNaMe'
        assert result['port'] == 40
        assert result['user'] is None
        assert result['password'] is None
        assert result['fullpath'] == '/test.php'
        assert result['path'] == '/'
        assert result['query'] == 'test.php'
        assert result['url'] == 'http://HoStNaMe:40/test.php'
        assert result['qsd'] == {}

        result = script.parse_url('HTTPS://user@hostname/test.py')
        assert result['schema'] == 'https'
        assert result['host'] == 'hostname'
        assert result['port'] is None
        assert result['user'] == 'user'
        assert result['password'] is None
        assert result['fullpath'] == '/test.py'
        assert result['path'] == '/'
        assert result['query'] == 'test.py'
        assert result['url'] == 'https://user@hostname/test.py'
        assert result['qsd'] == {}

        result = script.parse_url('  HTTPS://///user@@@hostname///test.py  ')
        assert result['schema'] == 'https'
        assert result['host'] == 'hostname'
        assert result['port'] is None
        assert result['user'] == 'user'
        assert result['password'] is None
        assert result['fullpath'] == '/test.py'
        assert result['path'] == '/'
        assert result['query'] == 'test.py'
        assert result['url'] == 'https://user@hostname/test.py'
        assert result['qsd'] == {}

        result = script.parse_url(
            'HTTPS://user:password@otherHost/full///path/name/',
        )
        assert result['schema'] == 'https'
        assert result['host'] == 'otherHost'
        assert result['port'] is None
        assert result['user'] == 'user'
        assert result['password'] == 'password'
        assert result['fullpath'] == '/full/path/name/'
        assert result['path'] == '/full/path/name/'
        assert result['query'] is None
        assert result['url'] == \
            'https://user:password@otherHost/full/path/name/'
        assert result['qsd'] == {}

        # Handle garbage
        assert script.parse_url(None) is None

        result = script.parse_url(
            'mailto://user:password@otherHost/lead2gold@gmail.com' +
            '?from=test@test.com&name=Chris%20Caron&format=text'
        )
        assert result['schema'] == 'mailto'
        assert result['host'] == 'otherHost'
        assert result['port'] is None
        assert result['user'] == 'user'
        assert result['password'] == 'password'
        assert unquote(result['fullpath']) == '/lead2gold@gmail.com'
        assert result['path'] == '/'
        assert unquote(result['query']) == 'lead2gold@gmail.com'
        assert unquote(result['url']) == \
            'mailto://user:password@otherHost/lead2gold@gmail.com'
        assert len(result['qsd']) == 3
        assert 'name' in result['qsd']
        assert unquote(result['qsd']['name']) == 'Chris Caron'
        assert 'from' in result['qsd']
        assert unquote(result['qsd']['from']) == 'test@test.com'
        assert 'format' in result['qsd']
        assert unquote(result['qsd']['format']) == 'text'

        # Test Passwords with question marks ?; not supported
        result = script.parse_url(
            'http://user:pass.with.?question@host'
        )
        assert result is None
        result = script.parse_url(
            'http://user@host?pass=pass.with.?question'
        )

        assert result['schema'] == 'http'
        assert result['host'] == 'host'
        assert result['port'] is None
        assert result['user'] == 'user'
        assert result['password'] == 'pass.with.?question'
        assert result['fullpath'] is None
        assert result['path'] is None
        assert result['query'] is None
        assert unquote(result['url']) == 'http://user:pass.with.?question@host'
        assert len(result['qsd']) == 1
        assert unquote(result['qsd']['pass']) == 'pass.with.?question'

    def test_parse_list(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)

        # A simple single array entry (As str)
        results = script.parse_list('.mkv,.avi,.divx,.xvid,' +
                                    '.mov,.wmv,.mp4,.mpg,.mpeg,.vob,.iso')

        assert len(results) == 11
        for x in ['.divx', '.iso', '.mkv', '.mov', '.mpg',
                  '.avi', '.mpeg', '.vob', '.xvid', '.wmv', '.mp4']:
            assert x in results

        # Now 2 lists with lots of duplicates and other delimiters
        results = script.parse_list(
            '.mkv,.avi,.divx,.xvid,.mov,.wmv,.mp4,.mpg .mpeg,.vob,,; ;',
            '.mkv,.avi,.divx,.xvid,' +
            '.mov        .wmv,.mp4;.mpg,.mpeg,.vob,.iso')

        assert len(results) == 11
        for x in ['.divx', '.iso', '.mkv', '.mov', '.mpg',
                  '.avi', '.mpeg', '.vob', '.xvid', '.wmv', '.mp4']:
            assert x in results

        # Now a list with extras we want to add as strings
        # empty entries are removed
        results = script.parse_list([
            '.divx', '.iso', '.mkv', '.mov', '', '  ',
            '.avi', '.mpeg', '.vob', '.xvid', '.mp4',
        ],
            '.mov,.wmv,.mp4,.mpg',
        )

        assert len(results) == 11
        for x in ['.divx', '.wmv', '.iso', '.mkv', '.mov',
                  '.mpg', '.avi', '.vob', '.xvid', '.mpeg', '.mp4']:
            assert x in results

    def test_parse_path_list01(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)

        # A simple single array entry (As str)
        results = script.parse_path_list(
            'C:\\test path with space\\and more spaces\\',
            'D:\\weird path\\more spaces\\ ',
            'D:\\weird path\\more spaces\\ G:\\save E:\\\\save_dir',
            'D:\\weird path\\more spaces\\ ',  # Duplicate is removed
            '  D:\\\\weird path\\more spaces\\\\ ',  # Duplicate is removed
            'relative path\\\\\\with\\crap\\\\ second_path\\more spaces\\ ',
            # Windows Network Paths
            '\\\\a\\network\\path\\\\ \\\\\\another\\nw\\\\path\\\\         ',
            # lists supported too
            ['relative path\\in\\list', 'second_path\\more spaces\\\\'],
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
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)

        # A simple single array entry (As str)
        results = script.parse_path_list(
            # 3 paths identified below
            '//absolute/path /another///absolute//path/// /',
            # A whole slew of duplicates and list inside list
            '/', ['/', '/', '//', '//////', ['/', ''], ],
            'relative/path/here',
            'relative/path/here/',
            'another/relative////path///',
        )
        assert len(results) == 5
        assert '/absolute/path' in results
        assert '/another/absolute/path' in results
        assert 'another/relative/path' in results
        assert '/' in results
        assert 'relative/path/here' in results

        results = script.parse_path_list(
            '/home/username/News/TVShows, /home/username/News/Movies',
        )
        assert len(results) == 2
        assert '/home/username/News/TVShows' in results
        assert '/home/username/News/Movies' in results

    def test_parse_path_list03(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)

        # A simple single array entry (As str)
        results = script.parse_path_list(
            '\\\\ht-pc\\htpc_5tb\\Media\\TV, ' +
            '\\\\ht-pc\\htpc_5tb\\Media\\Movies, ' +
            '\\\\ht-pc\\htpc_2tb\\Media\\TV, ' +
            '\\\\ht-pc\\htpc_2tb\\Media\\Movies',
        )
        assert len(results) == 4
        assert '\\\\ht-pc\\htpc_5tb\\Media\\TV' in results
        assert '\\\\ht-pc\\htpc_5tb\\Media\\Movies' in results
        assert '\\\\ht-pc\\htpc_2tb\\Media\\TV' in results
        assert '\\\\ht-pc\\htpc_2tb\\Media\\Movies' in results

    def test_parse_path_list04(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)

        # comma is a delimiter
        results = script.parse_path_list('path1, path2 ,path3,path4')
        assert len(results) == 4
        assert 'path1' in results
        assert 'path2' in results
        assert 'path3' in results
        assert 'path4' in results

    def test_parse_bool(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.parse_bool('Enabled', None) is True
        assert script.parse_bool('Disabled', None) is False
        assert script.parse_bool('Allow', None) is True
        assert script.parse_bool('Deny', None) is False
        assert script.parse_bool('Yes', None) is True
        assert script.parse_bool('YES', None) is True
        assert script.parse_bool('Always', None) is True
        assert script.parse_bool('No', None) is False
        assert script.parse_bool('NO', None) is False
        assert script.parse_bool('NEVER', None) is False
        assert script.parse_bool('TrUE', None) is True
        assert script.parse_bool('tRUe', None) is True
        assert script.parse_bool('FAlse', None) is False
        assert script.parse_bool('F', None) is False
        assert script.parse_bool('T', None) is True
        assert script.parse_bool('0', None) is False
        assert script.parse_bool('1', None) is True
        assert script.parse_bool('True', None) is True
        assert script.parse_bool('Yes', None) is True
        assert script.parse_bool(1, None) is True
        assert script.parse_bool(0, None) is False
        assert script.parse_bool(True, None) is True
        assert script.parse_bool(False, None) is False

        # only the int of 0 will return False since the function
        # casts this to a boolean
        assert script.parse_bool(2, None) is True
        # An empty list is still false
        assert script.parse_bool([], None) is False
        # But a list that contains something is True
        assert script.parse_bool(['value', ], None) is True

        # Use Default (which is False)
        assert script.parse_bool('OhYeah') is False
        # Adjust Default and get a different result
        assert script.parse_bool('OhYeah', True) is True

    def test_guesses(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)

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

        guess_keys = list(guess_dict.keys())
        guess_keys.remove('BadEntry')

        output = re.split(r'[\r\n]+', output)
        # Clean "" entry
        output = [x for x in filter(bool, output)]

        # Pushes are disabled in Standalone mode
        assert len(output) == 0

    def test_pushes(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)

        KEY = 'MY_VAR_TEST987'
        VALUE = 'MY_VALUE'

        # Value does not exist yet
        assert script.get(KEY) is None

        # Keep a handle on the real standard output
        stdout = sys.stdout
        sys.stdout = StringIO()
        script.push(KEY, VALUE)

        # extract data
        sys.stdout.seek(0)
        output = sys.stdout.read().strip()

        sys.stdout = stdout

        # Pushes are disabled in Standalone mode
        output = re.split(r'[\r\n]+', output)
        # Clean "" entry
        output = [x for x in filter(bool, output)]

        assert len(output) == 0
        assert script.get(KEY) == VALUE

    def test_validate(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.validate('TEMPDIR') is True
        # allow lowercase and mixed characters too
        assert script.validate('TempDir') is True

    def test_items(self):
        """see if we can retreive all our set variables using the items()
        function.
        """

        keypair = {
            'KEY1': 'val1',
            'KEY2': 'val2',
            'KEY3': 'val3',
            'KEY4': 'val4',
            'KEY5': 'val5',
        }

        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)
        for k, v in keypair.items():
            script.set(k, v)

        # Value doe snot exist yet
        for k, v in keypair.items():
            assert script.get(k) == v

        all_items = dict(script.items())
        for k, v in keypair.items():
            assert k in all_items
            assert script.get(k) == v

    def test_health(self):
        """ Test Health Checks
        """
        h = Health('%s/ALL' % Health.SUCCESS)
        assert h == (Health.SUCCESS, 'ALL')
        assert h.has_archive is False
        assert h.is_unpacked is True
        h = Health(('SUccESS', 'all'))
        assert h == (Health.SUCCESS, 'ALL')
        assert h.has_archive is False
        assert h.is_unpacked is True
        h = Health(Health.SUCCESS)
        assert h == (Health.SUCCESS, Health.DEFAULT_SUB)
        assert h.has_archive is False
        assert h.is_unpacked is True
        h = Health('BADKEYWORD')
        assert h == (Health.UNDEFINED, Health.DEFAULT_SUB)
        assert h.has_archive is True
        assert h.is_unpacked is True
        h = Health(Health.WARNING)
        assert h == (Health.WARNING, Health.DEFAULT_SUB)
        assert h.has_archive is True
        assert h.is_unpacked is False
        h = Health(Health.DELETED)
        assert h == (Health.DELETED, Health.DEFAULT_SUB)
        assert h.has_archive is False
        assert h.is_unpacked is False
        h = Health('')
        assert h == (Health.UNDEFINED, Health.DEFAULT_SUB)
        h = Health(None)
        assert h == (Health.UNDEFINED, Health.DEFAULT_SUB)

    def test_pid_file_control_01(self):
        """
        A Simple test that shows how multiple calls
        to is_unique_instance will not tamper with
        the PID-File or the process
        """

        # Define a simple script
        class SleepScript(ScriptBase):
            """
            A Simple sleeping script we'll thread for testing
            pid file generation
            """
            def main(self, *args, **kwargs):

                # Acquire lock
                self.lock.acquire()

                if not self.is_unique_instance(die_on_fail=False):
                    self.rlock.release()
                    self.lock.acquire()
                    return False

                if not self.is_unique_instance(die_on_fail=False):
                    self.rlock.release()
                    self.lock.acquire()
                    return False

                self.rlock.release()
                self.lock.acquire()
                return None

        def threaded_script(script):
            script._return_code = script.run()
            return

        # Script reference
        script = SleepScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        script.lock = Lock()
        script.rlock = Lock()
        script._return_code = None

        # Start locked
        script.lock.acquire()
        script.rlock.acquire()

        # Create our thread
        thread = Thread(target=threaded_script, args=(script, ))
        thread.start()

        # Let our script have control and await our turn
        script.lock.release()
        script.rlock.acquire()

        # Wait for our script to come close to exiting
        try:
            assert isfile(script.pidfile)

        except:
            # handle locks if we have a failure
            script.rlock.release()
            script.lock.release()
            thread.join()
            raise

        # Now let the threads exit gracefully
        script.lock.release()
        thread.join()

        # PID file tidys up nicely
        assert not isfile(script.pidfile)
        assert script._return_code == SHELL_EXIT_CODE.NONE

    def test_pid_file_control_02(self):
        """
        If the PID-File is pulled from under the process then
        it is treated as no longer being a unique process.

        We do things a little complicated when it isn't really nessisary.
        Hence this test uses threads to show it's possible. The main thing
        we're testing here however is that when we're done, we tidy up our
        own PID-File automatically.
        """

        # Define a simple script
        class SleepScript(ScriptBase):
            """
            A Simple sleeping script we'll thread for testing
            pid file generation
            """
            def main(self, *args, **kwargs):

                # Acquire lock
                self.lock.acquire()

                if not self.is_unique_instance(die_on_fail=False):
                    self.lock.acquire()
                    self.rlock.release()
                    return False

                # We want to pause here intentionally because
                # the test script is going to mess with the pid
                # file information for the lower processing
                self.rlock.release()
                self.lock.acquire()

                if not self.is_unique_instance(die_on_fail=False):
                    return False

                return None

        def threaded_script(script):
            script._return_code = script.run()
            return

        # Script reference
        script = SleepScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        script.lock = Lock()
        script.rlock = Lock()
        script._return_code = None

        # Start locked
        script.lock.acquire()
        script.rlock.acquire()

        # Create our thread
        thread = Thread(target=threaded_script, args=(script, ))
        thread.start()

        # Let our script have control and await our turn
        script.lock.release()

        script.rlock.acquire()
        # Wait for our script to come close to exiting
        try:
            assert isfile(script.pidfile)

        except:
            # handle locks if we have a failure
            script.lock.release()
            thread.join()
            raise

        # Remove this pidfile; this yanks the carpet from under it
        # causing it to treat the process as no longer being unique
        os.unlink(script.pidfile)

        script.lock.release()
        # Now let the threads exit gracefully
        thread.join()

        # PID file tidys up nicely
        assert not isfile(script.pidfile)
        assert script._return_code == SHELL_EXIT_CODE.FAILURE

    def test_pid_file_control_03(self):
        """
        This is the same as test_pid_file_control_02, we're basically
        going to change the modification time of the pid file which
        causes the script to no longer treat the process as unique

        We do things a little complicated when it isn't really nessisary.
        Hence this test uses threads to show it's possible. The main thing
        we're testing here however is that when there is a failure, the
        base script keeps the PID-File around if it's been tampered with.
        """

        # Define a simple script
        class SleepScript(ScriptBase):
            """
            A Simple sleeping script we'll thread for testing
            pid file generation
            """
            def main(self, *args, **kwargs):

                # Acquire lock
                self.lock.acquire()

                if not self.is_unique_instance(die_on_fail=False):
                    self.lock.acquire()
                    self.rlock.release()
                    return False

                # We want to pause here intentionally because
                # the test script is going to mess with the pid
                # file information for the lower processing
                self.rlock.release()
                self.lock.acquire()

                if not self.is_unique_instance(die_on_fail=False):
                    return False

                return None

        def threaded_script(script):
            script._return_code = script.run()
            return

        # Script reference
        script = SleepScript(logger=False, debug=VERY_VERBOSE_DEBUG)
        script.lock = Lock()
        script.rlock = Lock()
        script._return_code = None

        # Start locked
        script.lock.acquire()
        script.rlock.acquire()

        # Create our thread
        thread = Thread(target=threaded_script, args=(script, ))
        thread.start()

        # Let our script have control and await our turn
        script.lock.release()

        script.rlock.acquire()
        # Wait for our script to come close to exiting
        try:
            assert isfile(script.pidfile)

        except:
            # handle locks if we have a failure
            script.lock.release()
            thread.join()
            raise

        # At least 1 second has to elapse so the changed modification
        # time will show through
        sleep(1)

        # touch our pid file (causes the modification time to shift)
        # thus becoming different then what we are currently set to
        with open(script.pidfile, 'a'):
            os.utime(script.pidfile, None)

        script.lock.release()
        # Now let the threads exit gracefully
        thread.join()

        # PID file tidys up nicely
        assert not isfile(script.pidfile)
        assert script._return_code == SHELL_EXIT_CODE.FAILURE

    def test_pid_file_control_04(self):
        """
        If our PID is different then what was written in the
        PID-File, this also causes us to abort
        """

        # Script reference
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)
        assert script.pidfile is None
        assert script.is_unique_instance(die_on_fail=False) is True
        assert script.is_unique_instance(die_on_fail=False) is True
        assert script.is_unique_instance(die_on_fail=False) is True
        assert isfile(script.pidfile)

        # Change our PID so it won't match what is in the
        # PID-File; this should trigger a failure
        script.pid = 0

        assert script.is_unique_instance(die_on_fail=False) is False

        # PID-File should still be present!!
        assert isfile(script.pidfile)

    def test_parse_regex(self):
        # a NZB Logger set to False uses stderr
        script = ScriptBase(logger=False, debug=VERY_VERBOSE_DEBUG)

        # An invalid regular expression (bracket has no close)
        results = script.parse_regex(r'(.*\.mkv, ', simple=False)
        assert(len(results) == 0)

        results = script.parse_regex(r'.*\.mkv, .*\.avi,', simple=False)
        assert(len(results) == 2)

        # Now we'll scan our match and we should be okay
        assert(next((True for x in results
                     if x.match('test.mkv')), False) is True)

        # We're case sensitive too!
        assert(next((True for x in results
                     if x.match('test.MKV')), False) is True)

        assert(next((True for x in results
                     if x.match('test.aVi')), False) is True)

        # We don't match against other things not specified in our regular
        # expression
        assert(next((True for x in results
                     if x.match('test.iso')), False) is False)

        # The simple mode (is the default) and allows us to create our
        # regular expression easier using the old linux/windows commands
        # like ?? and *
        results = script.parse_regex('*.mkv, *.avi')
        assert(len(results) == 2)
