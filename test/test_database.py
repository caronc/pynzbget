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
from TestBase import TestBase
from TestBase import TEMP_DIRECTORY

from os import unlink
from os.path import join

from nzbget.Database import Database
from nzbget.Database import Category
from nzbget.Database import NZBGET_DATABASE_VERSION
from nzbget.Logger import VERY_VERBOSE_DEBUG

# Temporary Directory
DATABASE = join(TEMP_DIRECTORY, 'nzbget_test.db')

KEY = 'The.Perfect.Name.nzb'


class TestDatabase(TestBase):
    def teardown_method(self):
        """This method is run once after _each_ test method is executed"""
        try:
            unlink(DATABASE)
        except:
            pass

        # common
        super(TestDatabase, self).teardown_method()

    def test_schema_init(self):

        db = Database(
            container=KEY,
            database=DATABASE,
            reset=True,

            debug=VERY_VERBOSE_DEBUG,
        )
        assert db._get_version() == NZBGET_DATABASE_VERSION
        assert db._schema_okay()

    def test_key_manip(self):

        db = Database(
            container=KEY,
            database=DATABASE,
            reset=True,

            debug=VERY_VERBOSE_DEBUG,
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

            debug=VERY_VERBOSE_DEBUG,
        )
        assert db.get('MY_KEY') == 'MY_NEW_VALUE'
        assert db.get('MY_OTHER_KEY') == 'MY_OTHER_VALUE'

        # Removing
        assert db.unset('MY_OTHER_KEY')
        assert db.get('MY_OTHER_KEY', 'MISSING') == 'MISSING'

    def test_category_manip(self):

        db = Database(
            container=KEY,
            database=DATABASE,
            reset=True,

            debug=VERY_VERBOSE_DEBUG,
        )
        # New Keys
        assert db.set('MY_KEY', 'MY_VALUE')
        assert db.get('MY_KEY') == 'MY_VALUE'
        assert db.set('MY_KEY', 'MY_NEW_VALUE', category=Category.NZB)
        # No change in key
        assert db.get('MY_KEY') == 'MY_VALUE'
        # However, different category has different key mapped
        assert db.get('MY_KEY', category=Category.NZB) == 'MY_NEW_VALUE'

        # Updates
        assert db.set('MY_KEY', 'ANOTHER_VALUE', category=Category.NZB)
        assert db.get('MY_KEY', category=Category.NZB) == 'ANOTHER_VALUE'
        del db

        # Content saved across sessions
        db = Database(
            container=KEY,
            database=DATABASE,

            debug=VERY_VERBOSE_DEBUG,
        )
        assert db.get('MY_KEY') == 'MY_VALUE'
        assert db.get('MY_KEY', category=Category.NZB) == 'ANOTHER_VALUE'

    def test_key_purges01(self):

        db = Database(
            container=KEY,
            database=DATABASE,
            reset=True,

            debug=VERY_VERBOSE_DEBUG,
        )

        assert db.set('MY_KEY', 'MY_VALUE')
        assert db.get('MY_KEY') == 'MY_VALUE'

        assert db.set('MY_OTHER_KEY', 'MY_OTHER_VALUE')
        assert db.get('MY_OTHER_KEY') == 'MY_OTHER_VALUE'

        # purge entries (0 = all)

    def test_key_purges02(self):

        db = Database(
            container=KEY,
            database=DATABASE,
            reset=True,

            debug=VERY_VERBOSE_DEBUG,
        )

        assert db.set('MY_KEY', 'MY_VALUE')
        assert db.get('MY_KEY') == 'MY_VALUE'

        assert db.set('MY_OTHER_KEY', 'MY_OTHER_VALUE')
        assert db.get('MY_OTHER_KEY') == 'MY_OTHER_VALUE'

        # purge entries (0 = all)
        db.prune(0)
        assert db.get('MY_KEY') is None
        assert db.get('MY_OTHER_KEY') is None
