#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# SoundConverter - GNOME application for converting between audio formats.
# Copyright 2004 Lars Wirzenius
# Copyright 2005-2012 Gautier Portet
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3 of the License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

import time
import os
import urllib
import gnomevfs
from fileoperations import vfs_exists


class TargetNameGenerator:

    """Generator for creating the target name from an input name."""

    bad_chars = u'\\?%*:|"<>\ufffd'

    def __init__(self):
        self.folder = None
        self.subfolders = ''
        self.basename = '%(.inputname)s'
        self.ext = '%(.ext)s'
        self.suffix = None
        self.replace_messy_chars = False
        self.max_tries = 2
        self.exists = vfs_exists

    def get_target_name(self, sound_file):

        assert self.suffix, 'you just forgot to call set_target_suffix()'

        u = gnomevfs.URI(sound_file.uri)
        root, ext = os.path.splitext(u.path)

        root = sound_file.base_path
        basename, ext = os.path.splitext(urllib.unquote(sound_file.filename))

        # make sure basename constains only the filename
        basefolder, basename = os.path.split(basename)

        d = {
            '.inputname': basename,
            '.ext': ext,
            '.target-ext': self.suffix[1:],
            'album': _('Unknown Album'),
            'artist': _('Unknown Artist'),
            'title': basename,
            'track-number': 0,
            'track-count': 0,
            'genre': '',
            'year': '',
            'date': '',
            'disc-number': 0,
            'disc-count': 0,
        }
        for key in sound_file.tags:
            d[key] = sound_file.tags[key]
            if isinstance(d[key], basestring):
                # take care of tags containing slashes
                d[key] = d[key].replace('/', '-')

        # add timestamp to substitution dict -- this could be split into more
        # entries for more fine-grained control over the string by the user...
        timestamp_string = time.strftime('%Y%m%d_%H_%M_%S')
        d['timestamp'] = timestamp_string

        pattern = os.path.join(self.subfolders, self.basename + self.suffix)
        result = pattern % d

        if self.replace_messy_chars:
            # convert to unicode object to manage filename letter by letter
            if not isinstance(result, unicode):
                result = unicode(result, 'utf-8', 'replace')

            for char in self.bad_chars:
                result = result.replace(char, '_')

        # convert back to string so that urllib could cope with it
        if isinstance(result, unicode):
            result = result.encode('utf-8')

        if self.folder is None:
            folder = root
        else:
            folder = urllib.quote(self.folder, '/:')

        if '/' in pattern:
            # we are creating folders using tags, disable basefolder handling
            basefolder = ''

        result = os.path.join(folder, basefolder, urllib.quote(result))

        return result
