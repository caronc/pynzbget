# -*- encoding: utf-8 -*-
#
# A base scripting class used for NZBGet Scripts
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
"""
This script provides a base for all NZBGet Scripts and provides
functionality such as:
 * validate() - handle environment checking, correct versioning as well
                as if the expected configuration variables you specified
                are present.

 * push()     - pushes a variables to the NZBGet server


 * set()/get()- Hash table get/set attributes that can be set in one script
                and then later retrieved from another. get() can also
                be used to fetch content that was previously pushed using
                the push() tool. You no longer need to work with environment
                variables. If you enable the SQLite database, set content is
                put here as well so that it can be retrieved by another
                script.

 * get_api()  - Retreive a simple API/RPC object built from the global
                variables NZBGet passes into an external program when
                called.

 * get_files()- list all files in a specified directory as well as fetching
                their details such as filesize, modified date, etc in an
                easy to reference dictionary.  You can provide a ton of
                different filters to minimize the content returned. Filters
                can by a regular expression, file prefixes, and/or suffixes.

 * parse_nzbfile() - Parse an NZB-File and extract all of its meta
                     information from it. lxml must be installed on your
                     system for this to work correctly

 * parse_list() - Takes a string (or more) as well as lists of strings as
                  input. It then cleans it up and produces an easy to
                  manage list by combining all of the results into 1.
                  Hence: parse_list('.mkv, .avi') returns:
                      [ '.mkv', '.avi' ]

 * parse_bool() - Handles all of NZBGet's configuration options such as
                  'on' and 'off' as well as 'yes' or 'no', or 'True' and
                  'False'.  It greatly simplifies the checking of these
                  variables passed in from NZBGet

 * push_guess() - You can push a guessit dictionary (or one of your own
                  that can help identify your release for other scripts
                  to use later after yours finishes

 * pull_guess() - Pull a previous guess pushed by another script.
                  why redo grunt work if it's already done for you?
                  if no previous guess content was pushed, then an
                  empty dictionary is returned.

Ideally, you'll write your script using this class as your base wrapper
requiring you to only define a main() function and call run().
You no longer need to manage the different return codes NZBGet uses,
instead you can just return True, False and None from your main()
function and let the wrappers transform that to the proper return code.

Logging is automatically initialized and works right away.
When you define your logging, you can prepare in the following ways:
   logging=True
        All output will be redirected to stdout

   logging=False
        All output will be redirected to stderr
   logging=None
        No logging will take place
   logging=Logger()
        If you pass a Logger object (you already set up yourself), then
        logging will just reference that instance.
   logging=string
        The string you identify will be the log file content is written to
        with self rotating capabilties built in.  Man... life is so easy...

Additionally all exception handling is wrapped to make debugging easier.
"""

import re
from tempfile import gettempdir
from os import environ
from os import makedirs
from os import walk
from os.path import isdir
from os.path import join
from os.path import splitext
from getpass import getuser
from logging import Logger
from datetime import datetime

# Relative Includes
from NZBGetAPI import NZBGetAPI
from Logger import init_logger
from Logger import destroy_logger

# NZB Processing Support if lxml is installed
try:
    from lxml import etree
    from lxml.etree import XMLSyntaxError
except ImportError:
    # No panic, we just can't use nzbfile parsing
    pass

# Database Support if sqllite is installed
try:
    from Database import Database
except ImportError:
    # No panic, we just can't use database
    pass

# File Stats
from stat import ST_MTIME
from stat import ST_SIZE
from os import stat

# Some booleans that are read to and from nzbget
NZBGET_BOOL_TRUE = 'yes'
NZBGET_BOOL_FALSE = 'no'

class EXIT_CODE(object):
    """List of exit codes for post processing
    """
    PARCHECK_CURRENT = 91
    # Request NZBGet to do par-check/repair for current nzb-file.
    # This code can be used by pp-scripts doing unpack on their own.
    PARCHECK_ALL = 92
    # Post-process successful
    SUCCESS = 93
    # Post-process failed
    FAILURE = 94
    # Process skipped. Use this code when your script determines that it is
    # neither a success or failure. Perhaps your just not processing anything
    # due to how content was parsed.
    NONE = 95

EXIT_CODES = (
   EXIT_CODE.PARCHECK_CURRENT,
   EXIT_CODE.PARCHECK_ALL,
   EXIT_CODE.SUCCESS,
   EXIT_CODE.FAILURE,
   EXIT_CODE.NONE,
)

# Environment variables that identify specific configuration for scripts
SYS_ENVIRO_ID = 'NZBOP_'

# Script options
CFG_ENVIRO_ID = 'NZBPO_'

# Shared configuration options passed through NZBGet and push(); if these
# are found in the environment, they are saved to the `config` dictionary
SHR_ENVIRO_ID = 'NZBR_'

# DNZB is an environment variable sometimes referenced by other scripts
SHR_ENVIRO_DNZB_ID = '_DNZB_'

# GUESS is an environment variable sometimes referenced by other scripts
# it provides the guessed information for other scripts to save them
# from re-guessing all over again.
SHR_ENVIRO_GUESS_ID = '_GUESS_'

# NZBGet Internal Message Passing Prefix
NZBGET_MSG_PREFIX = '[NZB] '

# Precompile regular expressions for speed
SYS_OPTS_RE = re.compile('^%s([A-Z0-9_]+)$' % SYS_ENVIRO_ID)
CFG_OPTS_RE = re.compile('^%s([A-Z0-9_]+)$' % CFG_ENVIRO_ID)
SHR_OPTS_RE = re.compile('^%s([A-Z0-9_]+)$' % SHR_ENVIRO_ID)

# Precompile Guess Fetching
SHR_GUESS_OPTS_RE = re.compile('^%s([A-Z0-9_]+)$' % SHR_ENVIRO_GUESS_ID)

# This is used as a mapping table so when we fetch content later
# at another time we can map them to the same format commonly
# used.
GUESS_KEY_MAP = {
    'AUDIOCHANNELS': 'audioChannels', 'AUDIOCODEC': 'audioCodec',
    'AUDIOPROFILE': 'audioProfile', 'BONUSNUMBER':'bonusNumber',
    'BONUSTITLE': 'bonusTitle', 'CONTAINER':'container', 'DATE': 'date',
    'EDITION': 'edition', 'EPISODENUMBER': 'episodeNumber',
    'FILMNUMBER': 'filmNumber', 'FILMSERIES': 'filmSeries',
    'FORMAT': 'format', 'LANGUAGE': 'language',
    'RELEASEGROUP': 'releaseGroup',  'SCREENSIZE': 'screenSize',
    'SEASON': 'season', 'SERIES': 'series', 'SPECIAL': 'special',
    'SUBTITLELANGUAGE': 'subtitleLanguage', 'TITLE': 'title',
    'TYPE': 'type', 'VIDEOCODEC': 'videoCodec','VTYPE': 'vtype',
    'WEBSITE': 'website', 'YEAR': 'year',
}

# keys should not be complicated... make it so they aren't
VALID_KEY_RE = re.compile('[^a-zA-Z0-9_.-]')

# delimiters used to separate values when content is passed in by string
# This is useful when turning a string into a list
STRING_DELIMITERS = r'[\\\/\[\]\:;,\s]+'

# SQLite Database
NZBGET_DATABASE_FILENAME = "nzbget/nzbget.db"

class SCRIPT_MODE(object):
    # After the download of nzb-file is completed NZBGet can call
    # post-processing scripts (pp-scripts). The scripts can perform further
    # processing of downloaded files such es delete unwanted files
    # (*.url, etc.), send an e-mail notification, transfer the files to other
    # application and do any other things.
    POSTPROCESSING = 'postprocess'

    # Scan scripts are called when a new file is found in the incoming nzb
    # directory (option `NzbDir`). If a file is being added via web-interface
    # or via RPC-API from a third-party app the file is saved into nzb
    # directory and then processed. NZBGet loads only files with nzb-extension
    # but it calls the scan scripts for every file found in the nzb directory.
    # This allows for example for scan scripts which unpack zip-files
    # containing nzb-files.

    # To activate a scan script or multiple scripts put them into `ScriptDir`,
    # then choose them in the option `ScanScript`.
    SCAN = 'scan'

    # Queue scripts are called after the download queue was changed. In the
    # current version the queue scripts are called only after an nzb-file was
    # added to queue. In the future they can be calledon other events too.

    # To activate a queue script or multiple scripts put them into `ScriptDir`,
    # then choose them in the option `QueueScript`.
    QUEUE = 'queue'

    # Scheduler scripts are called by scheduler tasks (setup by the user).

    # To activate a scheduler script or multiple scripts put them into
    # `ScriptDir`, then choose them in the option `TaskX.Script`.
    SCHEDULER = 'scheduler'

# Depending on certain environment variables, a mode can be detected
# a mode can be used to. When using a MultiScript
SCRIPT_MODES = (
    SCRIPT_MODE.POSTPROCESSING,
    SCRIPT_MODE.SCAN,
    SCRIPT_MODE.QUEUE,
    SCRIPT_MODE.SCHEDULER,
)

class ScriptBase(object):
    """The intent is this is the script you run from within your script
       after overloading the main() function of your class
    """

    def __init__(self, database_key=None, logger=True, debug=False):
        # logger identifier
        self.logger_id = self.__class__.__name__
        self.logger = logger
        self.debug = debug

        # Script Mode
        self.script_mode = None

        # For Database Handling
        self.database = None
        self.database_key = database_key

        # Fetch System Environment (passed from NZBGet)
        self.system = dict([(SYS_OPTS_RE.match(k).group(1), v.strip()) \
            for (k, v) in environ.items() if SYS_OPTS_RE.match(k)])

        # Fetch/Load Script Specific Configuration
        self.config = dict([(CFG_OPTS_RE.match(k).group(1), v.strip()) \
            for (k, v) in environ.items() if CFG_OPTS_RE.match(k)])

        # Fetch/Load Shared Configuration through push()
        self.shared = dict([(SHR_OPTS_RE.match(k).group(1), v.strip()) \
            for (k, v) in environ.items() if SHR_OPTS_RE.match(k)])

        # Initialize information fetched from NZB-File
        self.nzbheaders = {}

        if 'TEMPDIR' not in self.system:
            self.system['TEMPDIR'] = join(
                gettempdir(),
                'nzbget-%s' % getuser(),
            )
            # enforce temporary directory
            environ['%sTEMPDIR' % SYS_ENVIRO_ID] = self.system['TEMPDIR']

        # Enabling DEBUG as a flag by specifying  near in the configuration
        # section of your script
        #Debug=no
        if self.debug is None:
            # Configure one
            try:
                self.debug = bool(int(self.system.get('DEBUG'), False))
            except:
                self.debug = False

        if isinstance(self.logger, basestring):
            # Use Log File
            self.logger = init_logger(
                name=self.logger_id,
                logger=logger,
                debug=debug,
            )

        elif not isinstance(self.logger, Logger):
            # handle all other types
            if logger is None:
                # None means don't log anything
                self.logger = init_logger(
                    name=self.logger_id,
                    logger=None,
                    debug=debug,
                )
            else:
                # Use STDOUT for now
                self.logger = init_logger(
                    name=self.logger_id,
                    logger=True,
                    debug=debug,
                )
        else:
            self.logger_id = None

        if not isdir(self.system['TEMPDIR']):
            try:
                makedirs(self.system['TEMPDIR'], 0700)
            except:
                self.logger.warning(
                    'Temporary directory could not be ' + \
                    'created: %s' % self.system['TEMPDIR'],
                )

        if self.debug:
            # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
            # Print Global System Varables to help debugging process
            # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
            for k, v in self.system.items():
                self.logger.debug('SYS %s=%s' % (k, v))

            for k, v in self.config.items():
                self.logger.debug('CFG %s=%s' % (k, v))

            for k, v in self.shared.items():
                self.logger.debug('SHR %s=%s' % (k, v))

        # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
        # Enforce system/global variables for script processing
        # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
        self.system['DEBUG'] = self.debug

        # Set environment variable how NZBGet Would have done so
        if self.debug:
            environ['%sDEBUG' % SYS_ENVIRO_ID] = NZBGET_BOOL_TRUE
        else:
            environ['%sDEBUG' % SYS_ENVIRO_ID] = NZBGET_BOOL_FALSE

    def __del__(self):
        if self.logger_id:
            destroy_logger(self.logger_id)

    def _push(self, key, value):
        """NZBGet has the ability to process certain messages
        delivered to it via stdout. This is just a wrapper
        script to ease this process

        This version of push is just used internally. It's designed
        To update system variables and only supports a specific
        set of commands which are predefined in the scripts that
        inherit this base class.

        users should be utlizing the push() command instead of
        this one.
        """
        # clean key
        key = VALID_KEY_RE.sub('', key).upper()

        # Push message on to nzbget
        print('%s%s=%s' % (
           NZBGET_MSG_PREFIX,
           key,
           value,
        ))
        return True

    def push(self, key, value):
        """Pushes a key/value pair to NZBGet Server

        The content pushed can be retrieved from
        self.config in scripts called after this one
        by the same key you specified in this script.
        """
        # clean key
        key = VALID_KEY_RE.sub('', key).upper()

        # Accomodate other environmental variables
        self.shared[key] = value
        if isinstance(value, bool):
            # convert boolean's to int's for consistency
            environ['%s%s' % (SHR_ENVIRO_ID, key)] = str(int(value))
        else:
            environ['%s%s' % (SHR_ENVIRO_ID, key)] = str(value)

        # Alert NZBGet of variable being set
        print('%s%s%s=%s' % (
           NZBGET_MSG_PREFIX,
           SHR_ENVIRO_ID,
           key,
           str(value),
        ))
        return True

    def push_guess(self, guess):
        """pushes guess results to NZBGet Server. The function was
        initially intended to provide a simply way of passing content
        from guessit(), but it can be used by any dictionary with
        common elements used to identify releases
        """

        if not isinstance(guess, dict):
            # A guess is a 'dict' type, so handle the common elements
            # if set.
            return False

        for key in sorted(guess.keys()):
            if key.upper() in GUESS_KEY_MAP.keys():
                # Push content to NZB Server
                self.push('%s%s' % (
                    SHR_ENVIRO_GUESS_ID,
                    key.upper(),
                ), str(guess[key]).strip())

        return True

    def pull_guess(self):
        """Retrieves guess content in a dictionary
        """
        # Fetch/Load Guess Specific Content
        guess = dict([
            (GUESS_KEY_MAP[SHR_GUESS_OPTS_RE.match(k).group(1)], v.strip()) \
            for (k, v) in self.shared.items() \
                if SHR_GUESS_OPTS_RE.match(k) and \
                SHR_GUESS_OPTS_RE.match(k).group(1) in GUESS_KEY_MAP])

        return guess

    def parse_nzbfile(self, nzbfile, push_dnzb=True):
        """Parse an nzbfile specified and return just the
        meta information within the <head></head> tags

        if push_dnzb is set to true, then the shared environment
        variables are pushed to the NZBGet server if parsing
        is successful
        """
        results = {}
        try:
            for event, element in etree.iterparse(
                nzbfile, tag="{http://www.newzbin.com/DTD/2003/nzb}head"):
                for child in element:
                    if child.tag == "{http://www.newzbin.com/DTD/2003/nzb}meta":
                        if child.text.strip():
                            # Only store entries with content
                            results[child.attrib['type'].upper()] = \
                                child.text.strip()

                            if push_dnzb:
                                # Push content to NZB Server
                                self.push('%s%s' % (
                                    SHR_ENVIRO_DNZB_ID,
                                    child.attrib['type'].upper(),
                                ), child.text.strip())

                element.clear()
            self.logger.info(
                'NZBParse - NZB-File parsed %d meta entries' % len(results),
            )

        except NameError:
            self.logger.warning('NZBParse - Skipped; lxml is not installed')

        except IOError:
            self.logger.error('NZBParse - NZB-File is missing: %s' % nzbfile)

        except XMLSyntaxError, e:
            if e[0] is None:
                # this is a bug with lxml in earlier versions
                # https://bugs.launchpad.net/lxml/+bug/1185701
                # It occurs when the end of the file is reached and lxml
                # simply just doesn't handle the closure properly
                # it was fixed here:
                # https://github.com/lxml/lxml/commit\
                #       /19f0a477c935b402c93395f8c0cb561646f4bdc3
                # So we can relax and return ok results here
                self.logger.info(
                    'NZBParse - NZB-File parsed %d meta entries' % \
                    len(results),
                )
            else:
                # This is the real thing
                self.logger.error(
                    'NZBParse - NZB-File is corrupt: %s' % nzbfile,
                )
                self.logger.debug('NZBParse - Exception %s' % str(e))

        return results

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # set() and get() wrappers
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    def set(self, key, value, notify_nzbget=True):
        """Sets a key/value pair into the configuration
        """
        # clean key
        key = VALID_KEY_RE.sub('', key).upper()

        self.logger.debug('set() %s=%s' % (key, value))
        if key in self.system:
            self.logger.warning('set() called using a system key (%s)' % key)

        # Save content to database
        if self.database is None and self.database_key:
            try:
                # Connect to database on first use only
                self.database = Database(
                    container=self.database_key,
                    database=join(
                        self.system['TEMPDIR'],
                        NZBGET_DATABASE_FILENAME,
                    ),
                    logger=self.logger,
                )
                self.logger.info('Connected to SQLite Database')

                # Database is ready to go
                if isinstance(value, bool):
                    self.database.set(key=key, value=int(value))
                else:
                    self.database.set(key=key, value=value)

            except NameError:
                # Sqlite wasn't installed
                # set the dbstore to false so it isn't used anymore
                self.database = False

        elif self.database_key:
            # Database is ready to go
            if isinstance(value, bool):
                self.database.set(key=key, value=int(value))
            else:
                self.database.set(key=key, value=value)

        # Set environmental variables
        self.config[key] = value

        # convert boolean's to int's for consistency
        if isinstance(value, bool):
            environ['%s%s' % (CFG_ENVIRO_ID, key)] = str(int(value))
        else:
            environ['%s%s' % (CFG_ENVIRO_ID, key)] = str(value)

        return True

    def get(self, key, default=None, check_system=True, check_shared=True):
        """works with set() operation making it easy to retrieve set()
        content
        """

        # clean key
        key = VALID_KEY_RE.sub('', key).upper()

        if check_system:
            # System variables over-ride all
            value = self.system.get('%s' % key)
            if value is not None:
                # only return if a key was found
                self.logger.debug('get(system) %s="%s"' % (key, value))
                return value

        value = self.config.get('%s' % key)
        if value is not None:
            # only return if a key was found
            self.logger.debug('get(config) %s="%s"' % (key, value))
            return value

        # Fetch content from database
        if self.database is None and self.database_key:
            try:
                # Connect to database on first use only
                self.database = Database(
                    container=self.database_key,
                    database=join(
                        self.system['TEMPDIR'],
                        NZBGET_DATABASE_FILENAME,
                    ),
                    logger=self.logger,
                )
                self.logger.info('Connected to SQLite Database')

                # Database is ready to go
                value = self.database.get(key=key)
                if value is not None:
                    # only return if a key was found
                    self.logger.debug('get(database) %s="%s"' % (key, value))
                    return value

            except NameError:
                # Sqlite wasn't installed
                # set the dbstore to false so it isn't used anymore
                self.database = False

        elif self.database_key:
            value = self.database.get(key=key)
            if value is not None:
                # only return if a key was found
                self.logger.debug('get(database) %s="%s"' % (key, value))
                return value

        # If we reach here, the content wasn't found in the database
        # or the database simply isn't enabled. We now fetch attempt to
        # fetch the content from it's shared variable now

        # We still haven't found the variable requested
        if check_shared:
            # We'll look for the shared environment variable now
            # These are set by the push() methods
            value = self.shared.get('%s' % key)
            if value is not None:
                self.logger.debug('get(shared) %s="%s"' % (key, value))
                return value

        self.logger.debug('get(default) %s=%s' % (key, str(default)))
        return default

    def validate(self, keys=None, min_version=11, *args, **kwargs):
        """validate against environment variables
        """

        # Initialize a global variable, we run through the entire function
        # so all errors can be caught to make it easier for debugging
        is_okay = True

        # version
        try:
            version = '%s.' % self.system.get('VERSION', '11')
            version = int(version.split('.')[0])
        except (TypeError, ValueError):
            version = 11

        if min_version > version:
            self.logger.error(
                'Validation - detected version %d, (min expected=%d)' % (
                    version, min_version)
            )
            is_okay = False

        if keys:
            missing = []
            if isinstance(keys, basestring):
                keys = self.parse_list(keys)

            missing = [
                key for key in keys \
                        if not (key in self.system or key in self.config)
            ]

            if missing:
                self.logger.error('Validation - Directives not set: %s' % \
                      ', '.join(missing))
                is_okay = False

        if not 'SCRIPTDIR' in self.system:
            self.logger.error(
                'Validation - (<v11) Directive not set: %s' % 'SCRIPTDIR',
            )
            is_okay = False

        if self.script_mode is not None and \
           hasattr(self, '%s_%s' % (self.script_mode, 'validate')):
            # This part of the validate() function preforms the
            # magic of supporting multiple script types by only
            # executing the validation script of the desiganted mode.
            #
            # it requires that developers write a unique validation
            # class per script type they want to support.
            #
            # hence: validate_postprocess() and validate_scheduler()

            # Call our validation script if it exists
            return getattr(
                self, '%s_%s' % (self.script_mode, 'validate'))(
                    keys=keys,
                    min_version=min_version,
                    *args, **kwargs
                )
        return is_okay

    def get_api(self):
        """This function can be used to return a XML-RCP server
        object using the server variables defined
        """

        # System Options required for RPC calls to work
        required_opts = (
            'CONTROLIP',
            'CONTROLPORT',
            'CONTROLUSERNAME',
            'CONTROLPASSWORD',
        )
        # Fetch standard RCP information to simplify future commands
        if set(self.system) & required_opts != required_opts:
            # Not enough options to extract RCP information
            return None

        # if we reach here, we have enough data to build an RCP connection
        host = self.system['CONTROLIP']
        if host == "0.0.0.0":
            host = "127.0.0.1"

        # Return API Controller
        return NZBGetAPI(
            self.system['CONTROLUSERNAME'],
            self.system['CONTROLPASSWORD'],
            host,
            self.system['CONTROLPORT'],
        )

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # File Retrieval
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    def get_files(self, search_dir, regex_filter=None, prefix_filter=None,
                    suffix_filter=None, fullstats=False):
        """Returns a dict object of the files found in the download
           directory. You can additionally pass in filters as a list or
           string) to filter the results returned.
              ex:
              {
                 '/full/path/to/file.mkv': {
                     'basename': 'file.mkv',
                     'dirname': '/full/path/to',
                     # always tolower() applied to:
                     'extension': mkv,

                     # If fullstatus == True then the following additional
                     # content is provided.

                     # filesize is in bytes
                     'filesize': 10000,
                     # modified date
                     'modified': datetime(),
                 }
              }

        """

        if not isdir(search_dir):
            return {}

        # Change all filters strings lists (if they aren't already)
        if regex_filter is None:
            regex_filter = tuple()
        if isinstance(regex_filter, basestring):
            regex_filter = (regex_filter,)
        elif isinstance(regex_filter, re._pattern_type):
            regex_filter = (regex_filter,)
        if suffix_filter is None:
            suffix_filter = tuple()
        if isinstance(suffix_filter, basestring):
            suffix_filter = (suffix_filter, )
        if prefix_filter is None:
            prefix_filter = tuple()
        if isinstance(prefix_filter, basestring):
            prefix_filter = (prefix_filter, )

        # clean prefix list
        if prefix_filter:
            prefix_filter = self.parse_list(prefix_filter)

        # clean up suffix list
        if suffix_filter:
            suffix_filter = self.parse_list(suffix_filter)

        # Precompile any defined regex definitions
        if regex_filter:
            _filters = []
            for f in regex_filter:
                if not isinstance(f, re._pattern_type):
                    try:
                        _filters.append(re.compile(f))
                        self.logger.debug('Compiled regex "%s"' % f)
                    except:
                        self.logger.error(
                            'invalid regular expression: "%s"' % f,
                        )
                        return {}
                else:
                    # precompiled already
                    _filters.append(f)
            # apply
            regex_filter = _filters

        # Build file list
        files = {}
        if not isdir(search_dir):
            return files

        for dname, dnames, fnames in walk(search_dir):
            for fname in fnames:
                filtered = False

                # Apply filters
                if regex_filter:
                    filtered = True
                    for regex in regex_filter:
                        if regex.search(fname):
                            self.logger.debug('Allowed %s (regex)' % fname)
                            filtered = False
                            break

                if not filtered and prefix_filter:
                    filtered = True
                    for prefix in prefix_filter:
                        if fname[0:len(prefix)] == prefix:
                            self.logger.debug('Allowed %s (prefix)' % fname)
                            filtered = False
                            break

                if not filtered and suffix_filter:
                    filtered = True
                    for suffix in suffix_filter:
                        if fname[-len(suffix):] == suffix:
                            self.logger.debug('Allowed %s (suffix)' % fname)
                            filtered = False
                            break

                if filtered:
                    continue

                # If we reach here, we store the file found
                extension = splitext(fname)[1].lower()
                _file = join(dname, fname)
                files[_file] = {
                    'basename': fname,
                    'dirname': dname,
                    'extension': extension,
                }

                if fullstats:
                    # Extend file information
                    stat_obj = stat(_file)
                    files[_file]['modified'] = \
                        datetime.fromtimestamp(stat_obj[ST_MTIME])
                    files[_file]['filesize'] = stat_obj[ST_SIZE]
        # Return all files
        return files

    def run(self, *args, **kwargs):
        """The intent is this is the script you run from within your script
        after overloading the main() function of your class
        """
        import traceback
        from sys import exc_info

        # Default
        main_function = self.main

        # Determine the function to use
        # multi-scripts need to define a
        #  - postprocess_main()
        #  - scan_main()
        #  - schedule_main()
        #  - queue_main()
        #
        # otherwise main() is executed
        if self.script_mode is not None and \
           hasattr(self, '%s_%s' % (self.script_mode, 'main')):
            main_function = getattr(
                self, '%s_%s' % (self.script_mode, 'main'))

        try:
            exit_code = main_function(*args, **kwargs)
        except:
            # Try to capture error
            exc_type, exc_value, exc_traceback = exc_info()
            lines = traceback.format_exception(
                     exc_type, exc_value, exc_traceback)
            self.logger.error('Fatal Exception:\n%s' % \
                ''.join('  ' + line for line in lines))
            exit_code = EXIT_CODE.FAILURE

        # Simplify return codes for those who just want to use
        # True/False/None
        if exit_code is None:
            exit_code = EXIT_CODE.NONE

        elif exit_code is True:
            exit_code = EXIT_CODE.SUCCESS

        elif exit_code is False:
            exit_code = EXIT_CODE.FAILURE

        # Otherwise Be specific and if the code is not a valid one
        # then simply swap it with the FAILURE one
        if exit_code not in EXIT_CODES:
            self.logger.error(
                'The exit code %d is not valid, ' % exit_code + \
                'changing response to a failure (%d).' % (EXIT_CODE.FAILURE),
            )
            exit_code = EXIT_CODE.FAILURE
        return exit_code

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    # Simplify Parsing
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    def parse_list(self, *args):
        """
        Take a string list and break it into a delimited
        list of arguments. This funciton also supports
        the processing of a list of delmited strings and will
        always return a unique set of arguments.

        You can append as many items to the argument listing for
        parsing.

        Hence: parse_list('.mkv, .iso, .avi') becomes:
            ['.mkv', '.iso', '.avi']

        Hence: parse_list('.mkv, .iso, .avi', ['.avi', '.mp4') becomes:
            ['.mkv', '.iso', '.avi', '.mp4']

        The parsing is very forgiving and accepts spaces, slashes, comma's
        semicolons, colons, and pipes as delimiters
        """

        result = []
        for arg in args:
            if isinstance(arg, basestring):
                result += re.split(STRING_DELIMITERS, arg)

            elif isinstance(arg, list) or isinstance(arg, tuple):
                for _arg in arg:
                    if isinstance(arg, basestring):
                        result += re.split(STRING_DELIMITERS, arg)
                    # A list inside a list? - use recursion
                    elif isinstance(_arg, list) or isinstance(_arg, tuple):
                        result += self.parse_list(_arg)
                    else:
                        # Convert whatever it is to a string and work with it
                        result += self.parse_list(str(_arg))
            else:
                # Convert whatever it is to a string and work with it
                result += self.parse_list(str(arg))

        # apply as well as make the list unique by converting it
        # to a set() first. filter() eliminates any empty entries
        return filter(bool, list(set(result)))

    def parse_bool(self, arg, default=False):
        """
        NZBGet uses 'yes' and 'no' as well as other strings such
        as 'on' or 'off' etch to handle boolean operations from
        it's control interface.

        This method can just simplify checks to these variables.

        If the content could not be parsed, then the default is
        returned.
        """

        if isinstance(arg, basestring):
            # no = no - False
            # of = short for off - False
            # 0  = int for False
            # fa = short for False - False
            # f  = short for False - False
            # n  = short for No - False
            if arg.lower()[0:2] in ('f', 'n', 'no', 'of', '0', 'fa'):
                return False
            # ye = yes - True
            # on = short for off - True
            # 1  = int for True
            # tr = short for True - True
            # t  = short for True - True
            elif arg.lower()[0:2] in ('t', 'y', 'ye', 'on', '1', 'tr'):
                return True
            # otherwise
            return default

        # Handle other types
        return bool(arg)

    def detect_mode(self):
        """
        Attempt to detect the script mode based on environment variables
        """
        # TODO
        return None

    def main(self, *args, **kwargs):
        """Write all of your code here making uses of your functions while
        returning your exit code
        """
        if not self.validate():
            # We're running a version < v11
            return False

        return True
