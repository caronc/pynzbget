# -*- encoding: utf-8 -*-
#
# A Test Suite (for nose) for an SQLite 3 wrapper Class written for NZBGet
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
import sys
from os import makedirs
from os import rmdir
from os import unlink
from os.path import dirname
from os.path import join
sys.path.insert(0, join(dirname(dirname(__file__)), 'nzbget'))

from Database import Database
from Database import NZBGET_DATABASE_VERSION

# Temporary Directory
from TestBase import TestBase
from TestBase import TEMP_DIRECTORY

DATABASE = join(TEMP_DIRECTORY, 'nzbget_test.db')

KEY = 'The.Perfect.Name.nzb'

class TestDatabase(TestBase):
    def tearDown(self):
        """Remove the database"""
        try:
            unlink(DATABASE)
        except:
            pass

        # common
        super(TestDatabase, self).tearDown()

    def cleanup(self):
        """Remove the database"""
        try:
            unlink(DATABASE)
        except:
            pass

        # common
        super(TestDatabase, self).cleanup()

    def test_schema_init(self):

        db = Database(
            container=KEY,
            database=DATABASE,
            reset=True,
        )
        assert db._get_version() == NZBGET_DATABASE_VERSION
        assert db._schema_okay()

    def test_key_manip(self):

        db = Database(
            container=KEY,
            database=DATABASE,
            reset=True,
        )
        # New Keys
        assert db.set('MY_KEY', 'MY_VALUE')
        assert db.get('MY_KEY') == 'MY_VALUE'
        # Updates
        assert db.set('MY_KEY', 'MY_NEW_VALUE')
        assert db.get('MY_KEY') == 'MY_NEW_VALUE'
        # Other Keys
        assert db.set('MY_OTHER_KEY', 'MY_OTHER_VALUE')
        assert db.get('MY_OTHER_KEY') == 'MY_OTHER_VALUE'

        del db
        # Content saved across sessions
        db = Database(
            container=KEY,
            database=DATABASE,
        )
        assert db.get('MY_KEY') == 'MY_NEW_VALUE'
        assert db.get('MY_OTHER_KEY') == 'MY_OTHER_VALUE'

    def test_key_purges(self):

        db = Database(
            container=KEY,
            database=DATABASE,
            reset=True,
        )

        assert db.set('MY_KEY', 'MY_VALUE')
        assert db.get('MY_KEY') == 'MY_VALUE'

        assert db.set('MY_OTHER_KEY', 'MY_OTHER_VALUE')
        assert db.get('MY_OTHER_KEY') == 'MY_OTHER_VALUE'

        # purge entries (0 = all)
        db.prune(0)
        assert db.get('MY_KEY') == None
        assert db.get('MY_OTHER_KEY') == None
