[![Tests](https://github.com/caronc/pynzbget/actions/workflows/tests.yml/badge.svg)](https://github.com/caronc/pynzbget/actions/workflows/tests.yml)
[![Paypal](https://img.shields.io/badge/paypal-donate-green.svg)](https://www.paypal.com/donate/?hosted_button_id=CR6YF7KLQWQ5E)

# pynzbget

pynzbget takes care of the boring parts of writing an
[NZBGet](https://nzbget.com) script, so you can focus on what your script
actually does. The same script can also run under
[SABnzbd](https://sabnzbd.org). It works with every NZBGet version back to
v11.

Some scripts that use it:
[Notify](https://github.com/caronc/nzb-notify),
[TidyIt](https://github.com/caronc/nzbget-tidyit),
[DirWatch](https://github.com/caronc/nzbget-dirwatch) and
[Subliminal](https://github.com/caronc/nzb-subliminal).

## Description

This provides a python framework to design NZBGet scripts with. The intent
was to greatly simplify the development and debugging process. It was
initially designed to work with NZBGet and is backwards compatible with all previous versions (as far back to v11). However it is also compatible with SABnzbd users too!

* It contains a built in meta tag parser to extract content from NZB-Files.
   _Note: This can only happen if lxml is installed on your system_.
* It can preform very basic obfuscation support on filenames that can not be
  interpreted.
* It creates a common SQLite database (optionally) to additionally write
  content passed via the set() function. This allows another script to later
  call get() and retrieve the data set() by another.
* It prepares logging right out of the box for you, there is no setup required
* All return codes have been simplified to None/True/False (you can still
  use the old ones if you want).
* It handles all of the exception handling. By this I mean, your code can throw
  an except and it's traceback will be captured gracefully to logging. Then the
  framework will look after returning a correct failure error code to NZBGet.
* It provides some very useful functions that are always being re-written
  inside of every other NZBGet script such as file scanning.
* It greatly simplifies the handling of environment variables and interaction
  to and from NZBGet.
* It can also be adapted to support SABnzbd scripting! Thus any script you write
  for NZBGet users, you can also tweak to work [with SABnzbd users too](https://github.com/caronc/pynzbget/wiki/SAB_PostProcessScripts)!
* It runs from a `lib/` folder bundled with your script, so your script
  works with the NZBGet v23+ Extension Manager (see below).

## Install

```bash
pip install pynzbget
```

You need Python 3.8 or newer.

## Documentation

For the most up to date information and API, visit the wiki at
* https://github.com/caronc/pynzbget/wiki

The entire framework was based on the information found here:
* [NZBGet](https://nzbget.com)
* [NZBGet Scripting Documentation](https://nzbget.com/documentation/extension-scripts/)
* [NZBGet Extension Manager](https://github.com/nzbgetcom/nzbget-extensions)
* [SABnzbd](https://sabnzbd.org/)
* [SABnzbd Scripting Documentation](https://sabnzbd.org/wiki/scripts/post-processing-scripts)

## Simplified Development

The following are some of the functionality that is built in for you:

 * __validate()__ - Handle environment checking, correct versioning as well
                as if the expected configuration variables you specified
                are present.

 * __health_check()__ - Checks the status of the retrieved content, currently
                this is only useful during Post-Processing.

 * __push()__ - Pushes a variables to the NZBGet server.


 * __set()/get()__ - Hash table get/set attributes that can be set in one script
                and then later retrieved from another. get() can also
                be used to fetch content that was previously pushed using
                the push() tool. You no longer need to work with environment
                variables. If you enable the SQLite database, set content is
                put here as well so that it can be retrieved by another
                script.

 * __unset()__    - This allows you to unset values set by set() and get() as well
                as ones set by push().

 * __nzb_set()__  - Similar to the set() function identified above except it
                is used to build an nzb meta hash table which can be later
                pushed to the server using push_dnzb().

 * __add_nzb()__  - Using the built in API/RPC NZBGet supports, this
                allows you to specify a path to an NZBFile which you want to
                enqueue for downloading.

 * __nzb_get()__  - Retieves NZB Meta information previously stored.

 * __nzb_unset()__ - Removes a variable previously set completely.

 * __get_statistics()__ - Using the built in API/RPC NZBGet supports, this
                retrieves and returns the statistics in an easy to ready
                dictionary  (_PostProcessScript_ only).

 * __get_logs()__ - Using the built in API/RPC NZBGet supports, this
                retrieves and returns the latest logs.

 * __get_files()__ - list all files in a specified directory as well as fetching
                their details such as filesize, modified date, etc in an
                easy to reference dictionary.  You can provide a ton of
                different filters to minimize the content returned. Filters
                can by a regular expression, file prefixes, and/or suffixes.

 * __parse_nzbfile()__ - Parse an NZB-File and extract all of its meta
                     information from it. lxml must be installed on your
                     system for this to work correctly.

 * __parse_list()__ - Takes a string (or more) as well as lists of strings as
                  input. It then cleans it up and produces an easy to
                  manage list by combining all of the results into 1.
                  Hence: parse_list('.mkv, .avi') returns:
                      [ '.mkv', '.avi' ]

 * __parse_path_list()__ - Very smilar to parse_list() except that it is used
                  to handle directory paths while cleaning them up at the
                  same time.

 * __parse_bool()__ - Handles all of NZBGet's configuration options such as
                  'on' and 'off' as well as 'yes' or 'no', or 'True' and
                  'False'.  It greatly simplifies the checking of these
                  variables passed in from NZBGet.


 * __push_guess()__ - You can push a guessit dictionary (or one of your own
                  that can help identify your release for other scripts
                  to use later after yours finishes.

 * __pull_guess()__ - Pull a previous guess pushed by another script.
                  why redo grunt work if it's already done for you?
                  if no previous guess content was pushed, then an
                  empty dictionary is returned.

 * __push_dnzb()__ - You can push all nzb meta information onbtained to
                  the NZBGet server as DNZB_ meta tags.

 * __pull_dnzb()__ - Pull all DNZB_ meta tags issued by the server and
                 return their values in a dictionary.
                  if no  DNZB_ (NZB Meta information) was found, then an
                  empty dictionary is returned instead.

 * __deobfuscate()__ - Take a filename and return it in a deobfuscated to the
                   best of its ability. (_PostProcessScript_ only)

 * __is_unique_instance()__ - Allows you to ensure your instance of your script is
                  unique. This is useful for Scheduled scripts which can be
                  called and then run concurrently with NZBGet.

## How To Use

* Developers are only required to define a class that inherits the NZBGet class
that identifies what they are attempting to write (_ScanScript_,
_PostProcessScript_, etc.).

* Then you write all of your code a the _main()_ you must define.

## Your First Script

Every NZBGet script starts with a header. NZBGet reads it to learn what
kind of script you wrote and which options to show in its settings page.
After that, you write a class with a `main()` and pynzbget does the rest.

Save this as `MyExtension.py`:

```python
#!/usr/bin/env python3
###########################################################################
### NZBGET POST-PROCESSING SCRIPT

# Says hello when a download finishes.
#
# Author: Your Name.
# Version: 1.0.0.
# License: GPLv3.
# Home: https://github.com/you/MyExtension

###########################################################################
### OPTIONS

# Who to greet.
#Name=World

# Enable debug logging (yes, no).
#Debug=no

### NZBGET POST-PROCESSING SCRIPT
###########################################################################
import sys
from os.path import abspath, dirname, join

# Look in lib/ for packages first (see "NZBGet Extension Manager" below)
sys.path.insert(0, join(dirname(abspath(__file__)), 'lib'))

from nzbget import PostProcessScript


class MyExtension(PostProcessScript):
    def main(self, *args, **kwargs):
        # Make sure we're running under NZBGet and our options are set
        if not self.validate(keys=('Name', )):
            # validate() already logged why
            return False

        # Read our option (NZBGet passes it in as NZBPO_NAME)
        name = self.get('Name', 'World')

        # Read details about the download (NZBPP_NZBNAME, NZBPP_DIRECTORY)
        nzbname = self.get('NZBNAME')
        directory = self.get('DIRECTORY')

        # Logging is ready to go
        self.logger.info(f'Hello {name}! {nzbname} is in {directory}')

        # All done
        return True


if __name__ == '__main__':
    # run() calls main() and turns its answer into an NZBGet exit code
    sys.exit(MyExtension().run())
```

Drop it into NZBGet's scripts folder and it shows up in the settings.

### What to Return

| Return  | Meaning                                              |
|---------|------------------------------------------------------|
| `True`  | Everything worked                                    |
| `False` | Something went wrong                                 |
| `None`  | Nothing to do, so you skipped it (not a failure)     |

You can still use NZBGet's own exit codes if you'd rather:

```python
from nzbget import EXIT_CODE

# Same as returning True
return EXIT_CODE.SUCCESS
```

## Script Types

Pick the class that matches the line in your header:

| Header line                         | Class                  |
|-------------------------------------|------------------------|
| `### NZBGET POST-PROCESSING SCRIPT` | `PostProcessScript`    |
| `### NZBGET SCHEDULER SCRIPT`       | `SchedulerScript`      |
| `### NZBGET QUEUE SCRIPT`           | `QueueScript`          |
| `### NZBGET SCAN SCRIPT`            | `ScanScript`           |
| `### NZBGET FEED SCRIPT`            | `FeedScript`           |
| SABnzbd post-processing             | `SABPostProcessScript` |

Each type gets its own set of values from NZBGet. You read them all with
`get()`, leaving off the prefix NZBGet puts in front of them.

### Post Process Script Example
```python
#############################################################################
### NZBGET POST-PROCESSING SCRIPT                                         ###
#
# Author: Your Name Goes Here <your@email.address>
#
# Describe your Post-Process Script here
#

############################################################################
### OPTIONS                                                              ###

#
# Enable NZBGet debug logging (yes, no)
#Debug=no
#

### NZBGET POST-PROCESSING SCRIPT                                         ###
#############################################################################

from nzbget import PostProcessScript

# Now define your class while inheriting the rest
class MyPostProcessScript(PostProcessScript):
    def main(self, *args, **kwargs):
        # write all of your code here you would have otherwise put in the
        # script

        if not self.validate():
            # No need to document a failure, validate will do that
            # on the reason it failed anyway
            return False

        # All system environment variables (NZBOP_.*) as well as Post
        # Process script specific content (NZBPP_.*)
        # following dictionary (without the NZBOP_ or NZBPP_ prefix):
        print('DIRECTORY %s' % self.get('DIRECTORY'))
        print('NZBNAME %s' % self.get('NZBNAME'))
        print('NZBFILENAME %s' % self.get('NZBFILENAME'))
        print('CATEGORY %s' % self.get('CATEGORY'))
        print('TOTALSTATUS %s' % self.get('TOTALSTATUS'))
        print('STATUS %s' % self.get('STATUS'))
        print('SCRIPTSTATUS %s' % self.get('SCRIPTSTATUS'))

        # Set any variable you want by any key. Note that if you use
        # keys that were defined by the system (such as CATEGORY, DIRECTORY,
        # etc, you may have some undesirable results. Try to avoid reusing
        # system variables already defined (identified above):
        self.set('MY_KEY', 'MY_VALUE')

        # You can fetch it back; this will also set an entry in  the
        # sqlite database for each hash references that can be pulled from
        # another script that simply calls self.get('MY_VAR')
        print(self.get('MY_KEY'))  # prints MY_VALUE

        # You can also use push() which is similar to set()
        # except that it interacts with the NZBGet Server and does not use
        # the sqlite database. This can only be reached across other
        # scripts if the calling application is NZBGet itself
        self.push('ANOTHER_KEY', 'ANOTHER_VALUE')

        # You can still however locally retrieve what you set using push()
        # with the get() function
        print(self.get('ANOTHER_KEY'))  # prints ANOTHER_VALUE

        # Your script configuration files (NZBPP_.*) are here in this
        # dictionary (again without the NZBPP_ prefix):
        # assume you defined `Debug=no` in the first 10K of your PostProcessScript
        # NZBGet translates this to `NZBPP_DEBUG` which can be retrieved
        # as follows:
        print('DEBUG %s' % self.get('DEBUG'))

        # Returns have been made easy. Just return:
        #   * True if everything was successful
        #   * False if there was a problem
        #   * None if you want to report that you've just gracefully
        #     skipped processing (this is better then False)
        #     in some circumstances. This is neither a failure or a
        #     success status.

        # Feel free to use the actual exit codes as well defined by
        # NZBGet on their website. They have also been defined here
        # from nzbget import EXIT_CODE

        return True

# Call your script as follows:
if __name__ == "__main__":
    from sys import exit

    # Create an instance of your Script
    ppscript = MyPostProcessScript()

    # call run() and exit() using it's returned value
    exit(ppscript.run())
```

### Scan Script Example
```python
############################################################################
### NZBGET SCAN SCRIPT                                                   ###
#
# Author: Your Name Goes Here <your@email.address>
#
# Describe your Scan Script here
#

############################################################################
### OPTIONS                                                              ###

#
# Enable NZBGet debug logging (yes, no)
#Debug=no
#

### NZBGET SCAN SCRIPT                                                   ###
############################################################################

from nzbget import ScanScript

# Now define your class while inheriting the rest
class MyScanScript(ScanScript):
    def main(self, *args, **kwargs):
        # write all of your code here you would have otherwise put in the
        # script

        if not self.validate():
            # No need to document a failure, validate will do that
            # on the reason it failed anyway
            return False

        # All system environment variables (NZBOP_.*) as well as Post
        # Process script specific content (NZBNP_.*)
        # following dictionary (without the NZBOP_ or NZBNP_ prefix):
        print('DIRECTORY %s' % self.get('DIRECTORY'))
        print('FILENAME %s' % self.get('FILENAME'))
        print('NZBNAME %s' % self.get('NZBNAME'))
        print('CATEGORY %s' % self.get('CATEGORY'))
        print('PRIORITY %s' % self.get('PRIORITY'))
        print('TOP %s' % self.get('TOP'))
        print('PAUSED %s' % self.get('PAUSED'))

        return True

# Call your script as follows:
if __name__ == "__main__":
    from sys import exit

    # Create an instance of your Script
    scanscript = MyScanScript()

    # call run() and exit() using it's returned value
    exit(scanscript.run())
```

### Scheduler Script Example
```python
############################################################################
### NZBGET SCHEDULER SCRIPT                                               ###
#
# Describe your Schedule Script here
# Author: Your Name Goes Here <your@email.address>
#

############################################################################
### OPTIONS                                                              ###

#
# Enable NZBGet debug logging (yes, no)
#Debug=no
#

### NZBGET SCHEDULER SCRIPT                                              ###
############################################################################

from nzbget import SchedulerScript

# Now define your class while inheriting the rest
class MySchedulerScript(SchedulerScript):
    def main(self, *args, **kwargs):

        # Version Checking, Environment Variables Present, etc
        if not self.validate():
            # No need to document a failure, validate will do that
            # on the reason it failed anyway
            return False

        # write all of your code here you would have otherwise put in the
        # script

        # All system environment variables (NZBOP_.*) as well as Post
        # Process script specific content (NZBSP_.*)
        # following dictionary (without the NZBOP_ or NZBSP_ prefix):
        print('DESTDIR %s' % self.get('DESTDIR'))

        return True
# Call your script as follows:
if __name__ == "__main__":
    from sys import exit

    # Create an instance of your Script
    myscript = MySchedulerScript()

    # call run() and exit() using it's returned value
    exit(myscript.run())
```

### MultiScript Example
```python
############################################################################
### NZBGET POST-PROCESSING/SCHEDULER SCRIPT                              ###
#
# Describe your Multi Script here
#
# Author: Your Name Goes Here <your@email.address>
#

############################################################################
### OPTIONS                                                              ###

#
# Enable NZBGet debug logging (yes, no)
#Debug=no
#

### NZBGET POST-PROCESSING/SCHEDULER SCRIPT                              ###
############################################################################

from nzbget import PostProcessScript
from nzbget import SchedulerScript

# Now define your class while inheriting the rest
class MyMultiScript(PostProcessScript, SchedulerScript):

    def postprocess_main(self, *args, **kwargs):

        # Version Checking, Environment Variables Present, etc
        if not self.validate():
            # No need to document a failure, validate will do that
            # on the reason it failed anyway
            return False

        # write your main function for your Post Processing

        return True

    def scheduler_main(self, *args, **kwargs):

        # Version Checking, Environment Variables Present, etc
        if not self.validate():
            # No need to document a failure, validate will do that
            # on the reason it failed anyway
            return False

        # write your main function for your Post Processing

        return True

# Call your script as follows:
if __name__ == "__main__":
    from sys import exit

    # Create an instance of your Script
    myscript = MyMultiScript()

    # call run() and exit() using it's returned value
    exit(myscript.run())
```

### Queue Script

Runs when something happens in the download queue. List the events you
care about under your header line:

```python
### NZBGET QUEUE SCRIPT
### QUEUE EVENTS: NZB_ADDED, NZB_DOWNLOADED

from nzbget import QueueEvent
from nzbget import QueueScript


class MyQueueScript(QueueScript):
    def main(self, *args, **kwargs):
        if not self.validate():
            return False

        # Which event woke us up
        if self.event != QueueEvent.NZB_ADDED:
            # Not one we care about
            return None

        # The download that was just added (NZBNA_NZBNAME)
        self.logger.info(f'Queued: {self.get("NZBNAME")}')
        return True
```

## Functions You Can Use

All of these are available as `self.<name>()` inside your script.

### Checking Things

```python
# Make sure we're running under NZBGet (v11 or newer) and these options
# were set in the settings page
if not self.validate(keys=('VideoPaths', 'Mode')):
    return False

# Post-processing only: did the download, repair and unpack go well?
if not self.health_check():
    return None

# Only allow one copy of this script to run at a time
if not self.is_unique_instance():
    return None
```

### Reading and Saving Values

```python
# Read an option, with a default if it's missing
mode = self.get('Mode', 'Preview')

# Save a value; scripts that run after yours (for the same download) can
# get() it too
self.set('MY_KEY', 'some value')

# Remove it again
self.unset('MY_KEY')

# Loop over everything get() can see
for key, value in self.items():
    self.logger.debug(f'{key} = {value}')

# Send a value to NZBGet itself so other scripts see it there too
# (NZBGet only; set() works everywhere)
self.push('ANOTHER_KEY', 'another value')
```

Post-processing, queue and scan scripts also keep `set()` values in a
small SQLite database (one per download), so they're still there for the
next script. Other script types can turn this on by passing
`database_key='my-key'` when they create the script.

### NZB Details

NZB-Files can carry extra details (meta tags) such as the show name or
category. These work like `get()` and `set()`, but for those details:

```python
# Read, change or remove a detail
category = self.nzb_get('category')
self.nzb_set('propername', 'My Show')
self.nzb_unset('episodename')

# Loop over them all
for key, value in self.nzb_items():
    self.logger.debug(f'{key} = {value}')

# Send our details to NZBGet (as DNZB_*), or read the ones it has
self.push_dnzb()
details = self.pull_dnzb()

# Read the details straight from an NZB-File
details = self.parse_nzbfile('/path/to/file.nzb')
```

`push_guess()` and `pull_guess()` do the same for "what is this download"
details (such as a [guessit](https://github.com/guessit-io/guessit)
result), so the next script doesn't have to work it out again:

```python
# One script figures out what the download is (NZBGet only)...
self.push_guess({'type': 'episode', 'title': 'My Show', 'season': 1})

# ...and a later one reuses it (an empty dict if nothing was pushed)
guess = self.pull_guess()
```

### Working With Files

```python
# Find files; you get back a dict keyed by each file's path
videos = self.get_files(
    '/path/to/search',
    suffix_filter=['.mkv', '.avi'],  # only these endings
    fullstats=True,                  # include size and dates
    max_depth=2,                     # don't go too deep
)

for path, info in videos.items():
    self.logger.info(f'{path} is {info["filesize"]} bytes')

# Post-processing only: give a scrambled file name a proper one
filename = self.deobfuscate('/path/to/download/a8b7c6d5e4.mkv')
```

`get_files()` can also filter with `regex_filter=` and `prefix_filter=`.
Each filter takes one value or a list.

### Turning Option Text Into Python

```python
# 'yes', 'on', 'true' and '1' become True; 'no', 'off' and so on are False
keep = self.parse_bool(self.get('KeepDirectories', 'no'))

# '.mkv, .avi .mp4' becomes a list of '.mkv', '.avi' and '.mp4'
# (duplicates are removed, so the order isn't kept)
extensions = self.parse_list(self.get('VideoExtensions'))

# Like parse_list(), but for folders (spaces in names are fine)
paths = self.parse_path_list(self.get('VideoPaths'))

# '*.iso, *.avi' becomes a list of compiled regular expressions
patterns = self.parse_regex('*.iso, *.avi', simple=True)

# Break a URL into its parts: schema, host, port, user, password, path...
url = self.parse_url('http://user:pass@localhost:8080/path')
```

Two more helpers live in `nzbget.Utils`:

```python
from nzbget.Utils import os_path_split
from nzbget.Utils import tidy_path

# Clean up a path: tidy_path('/path//to/dir/') gives '/path/to/dir'
path = tidy_path('/path//to/dir/')

# Split a path into its parts: ['', 'path', 'to', 'dir']
parts = os_path_split('/path/to/dir')
```

### Talking to NZBGet

These use NZBGet's API. pynzbget connects for you using NZBGet's own
settings.

```python
# Hand an NZB-File to NZBGet to download
self.add_nzb('/path/to/file.nzb', category='tv')

# Read the latest log lines
for line in self.get_logs(max_lines=100):
    self.logger.debug(line)

# Post-processing only: download, repair and unpack times and speeds
stats = self.get_statistics()
self.logger.info(f'Downloaded {stats["download_size_mb"]} MB')
```

## SABnzbd

Write your class with `SABPostProcessScript` (or alongside
`PostProcessScript`) and the same `get()` calls keep working. See the
[SABnzbd wiki page](https://github.com/caronc/pynzbget/wiki/SAB_PostProcessScripts)
for details.

## NZBGet Extension Manager

NZBGet v23 and newer can install scripts from its **Extension Manager**.
An extension is just a folder (shipped as a zip) like this:

```text
MyExtension/
    MyExtension.py
    manifest.json   # tells NZBGet about your script and its options
    lib/            # every package your script needs, pynzbget included
```

NZBGet won't run `pip` for you, so `lib/` has to come with the script:

```bash
# Install your packages into lib/, picking versions that work on Python 3.8
pip install --target MyExtension/lib --python-version 3.8 \
    --only-binary :all: -r requirements.txt

# pynzbget works without lxml, and lxml only runs where it was built
rm -rf MyExtension/lib/lxml MyExtension/lib/lxml-*.dist-info
```

The `sys.path.insert(...)` line in the example above is what lets your
script find `lib/`. Keep it above your other imports.

Write `manifest.json` once by hand, using your script's header as the guide.
Keep the header too; older NZBGet versions still read it. The
[manifest format](https://github.com/nzbgetcom/nzbget-extensions) is
documented by the NZBGet team.

## Development

```bash
# Run the tests
tox -e qa

# Run the tests without lxml (how extensions run it)
tox -e minimal

# Check for lint problems (tox -e format fixes what it can)
tox -e lint
```

Packaging:

```bash
# Remove old builds and caches
tox -e clean

# Build the source package and wheel into dist/
tox -e build

# Build the RPMs for RHEL/Rocky 9 and 10 and Fedora 44 (needs docker);
# they land in dist/rpm/
tox -e rpm

# Do everything a release needs: clean, lint, test, build, check the
# packages and build the source RPM
tox -e release
```
