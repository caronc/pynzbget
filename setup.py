# Copyright (C) 2026 Chris Caron <lead2gold@gmail.com>
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
# Everything about the package lives in pyproject.toml. This small file is
# only here for RHEL 9 and older, whose setuptools is too old to read
# pyproject.toml; packaging/redhat/python-nzbget.spec uses it there.
import os
import re

from setuptools import find_packages
from setuptools import setup


def read_version():
    """Read __version__ from nzbget/__init__.py."""
    with open(os.path.join('nzbget', '__init__.py'), encoding='utf-8') as f:
        for line in f:
            match = re.match(r'^__version__\s*=\s*[\'"]([^\'"]+)', line)
            if match:
                return match.group(1)

    raise RuntimeError('Version not found')


setup(
    name='pynzbget',
    version=read_version(),
    packages=find_packages(include=['nzbget*']),
)
