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

from juicer.common import Constants
from juicer.log import Log
import magic
import os.path
import re


class RPM(object):
    def __init__(self, source):
        self.name = os.path.basename(source)
        # Source is the original location of this RPM. That includes
        # both http://.... RPMs and local /home/user/... RPMs.
        self.source = source

        # Assume RPM is local.
        self.path = os.path.abspath(source)
        self.synced = True

        # If the RPM is remote, let's change what we know.
        url_regex = re.compile(r'^(http)s?://')
        if url_regex.match(self.source):
            self.path = None
            self.synced = False

    def verify(self):
        verified = False
        if not self.synced:
            verified = True
        else:
            mime = magic.from_file(self.path)
            if 'rpm' in mime.lower():
                verified = True
        return verified

    def sync(self, destination):
        dest_file = os.path.join(destination, self.name)

        # This is the case with stuff that already exists locally
        if self.synced and self.source:
            pass

        if not os.path.exists(destination):
            os.mkdir(destination)

        self.path = dest_file
        Log.log_debug("Beginning remote->local sync: %s->%s" % (self.source, self.path))
        juicer.utils.save_url_as(self.source, dest_file)
        self.modified = True
        self.synced = True

    def __str__(self):
        return self.path if self.path else self.source
