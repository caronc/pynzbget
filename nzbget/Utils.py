# -*- encoding: utf-8 -*-
#
# Some common utilities that may prove useful when processing downloads
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
import re
def os_path_split(path):
    """splits a path into a list (by it's path delimiter

       hence: split_path('/etc/test/file') outputs:
                ['', 'etc', 'test', 'file']

       relative paths don't have the blank entry at the head
       of the string:
       hence: split_path('relative/file') outputs:
                ['relative', 'file']

       Paths can be reassembed as follows:
       assert '/'.join(split_path('/etc/test/file')) == \
               '/etc/test/file'

       assert '/'.join(split_path('relative/file')) == \
               'relative/file'
    """
    p_list = re.split('[%s]+' % re.escape('\\/'), path)
    while not p_list[-1]:
        p_list.pop()
    return p_list
