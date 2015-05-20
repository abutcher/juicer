# -*- coding: utf-8 -*-
# Juicer - Administer Pulp and Release Carts
# Copyright © 2015, Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bitmath
import logging
import magic
import os.path
import progressbar
import re
import urllib2

from juicer.common import Constants


class CartItem(object):
    def __init__(self, source):
        self.output = logging.getLogger('juicer')
        self.name = os.path.basename(source)
        # Source is the original location of this file. That includes
        # both http://.... files and local /home/user/... files.
        self.source = source

        # Assume item is local.
        self.path = os.path.abspath(source)
        self.synced = True

        # If the item is remote, let's change what we know.
        url_regex = re.compile(r'^(http)s?://')
        if url_regex.match(self.source):
            self.path = None
            self.synced = False

        self.item_type = self._set_item_type() if self.path else None

    def _set_item_type(self):
        mime_type = magic.from_file(self.path).lower()
        item_type = None
        if 'rpm' in mime_type:
            item_type = 'rpm'
        elif 'tar' in mime_type:
            item_type = 'docker_image'
        return item_type

    def sync(self, destination):
        dest_file = os.path.join(destination, self.name)

        # This is the case with stuff that already exists locally
        if self.synced and self.source:
            pass

        if not os.path.exists(destination):
            os.mkdir(destination)

        self.path = dest_file
        self.output.debug("Beginning remote->local sync: %s->%s" % (self.source, self.path))

        # An array of widgets to design our progress bar.
        widgets = ['Downloading %s ' % self.name,
                   progressbar.Percentage(), ' ',
                   progressbar.Bar(marker=progressbar.RotatingMarker()), ' ',
                   progressbar.ETA(), ' ',
                   bitmath.integrations.BitmathFileTransferSpeed()]

        u = urllib2.urlopen(self.source)
        f = open(self.path, 'wb')
        meta = u.info()
        item_size = int(meta.getheaders("Content-Length")[0])
        pbar = progressbar.ProgressBar(
            widgets=widgets,
            maxval=item_size).start()
        downloaded = 0
        while True:
            buffer = u.read(Constants.DOWNLOAD_AT_ONCE)
            if not buffer:
                break
            f.write(buffer)
            downloaded += len(buffer)
            if downloaded < pbar.maxval:
                pbar.update(int(downloaded))
        f.close()
        pbar.finish()

        self.modified = True
        self.synced = True
        self.item_type = self._set_item_type()

    def __str__(self):
        return self.path if self.path else self.source
