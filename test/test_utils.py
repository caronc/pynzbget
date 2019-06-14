# -*- encoding: utf-8 -*-
#
# A Test Suite (for nose) for an SQLite 3 wrapper Class written for NZBGet
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
import sys
from os.path import dirname
from os.path import join
sys.path.insert(0, join(dirname(dirname(__file__)), 'nzbget'))

from Utils import os_path_split
from Utils import tidy_path
from TestBase import TestBase


class TestUtils(TestBase):
    def test_os_path_split(self):
        assert os_path_split('C:\\My Directory\\SubDirectory') == [
            'C:',
            'My Directory',
            'SubDirectory',
        ]
        assert os_path_split('relative/nix/pathname') == [
            'relative',
            'nix',
            'pathname',
        ]
        assert os_path_split('/absolute/nix/pathname') == [
            '',
            'absolute',
            'nix',
            'pathname',
        ]
        assert os_path_split('') == []
        assert os_path_split('/') == ['', ]
        assert os_path_split('\\') == ['', ]

        # Weird Paths are fixed
        assert os_path_split('///////////') == ['', ]
        assert os_path_split('\\\\\\\\\\') == ['', ]

        # Trailing slashes are removed
        assert os_path_split('relative/nix/pathname/') == [
            'relative',
            'nix',
            'pathname',
        ]

    def test_tidy_path(self):

        # No Change
        assert tidy_path('C:\\My Directory\\SubDirectory') == \
            'C:\\My Directory\\SubDirectory'

        assert tidy_path('C:\\\\\My Directory\\\\\\SubDirectory  ') == \
            'C:\\My Directory\\SubDirectory'

        assert tidy_path('C:\\') == 'C:\\'
        assert tidy_path('C:\\\\\\') == 'C:\\'
        assert tidy_path('/') == '/'
        assert tidy_path('///////////') == '/'
        assert tidy_path('////path///////') == '/path'
        assert tidy_path('////path/with spaces//////') == \
            '/path/with spaces'

        # Network Paths
        assert tidy_path('\\\\network\\\\path\\ ') == \
            '\\\\network\\path'
