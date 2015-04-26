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

import hashlib
from juicer.log import Log
import magic
import os.path
import pyrpm.rpm
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

    def upload_data(self, checksum_type='sha256'):
        # We can't get any data from a remote rpm.
        # if not self.synced:
        #    self.sync()

        try:
            rpm_file = open(self.path, 'rb')
        except IOError as e:
            Log.log_info("Error opening RPM %s: %s", self.path, e.strerror)

        rpm = pyrpm.rpm.RPM(rpm_file)

        data = {
            'unit_key': {
                'arch': rpm.header.architecture,
                'checksum': getattr(hashlib, checksum_type)(self.path).hexdigest(),
                'checksum_type': checksum_type,
                'epoch': 0,
                'name': rpm.header.name,
                'package_basename': self.name,
                'release': rpm.header.release,
                'size': os.path.getsize(self.path),
                'version': rpm.header.version
            },
            'unit_metadata': {
                'description': rpm.header.description,
                'filename': self.name,
                'license': rpm.header.license,
                'relativepath': self.name,
                'vendor': rpm.header.vendor
            }
        }
        return data

    def sync(self, destination):
        dest_file = os.path.join(destination, self.name)

        # This is the case with stuff that already exists locally
        if self.synced and self.source:
            pass

        if not os.path.exists(destination):
            os.mkdir(destination)

        self.path = dest_file
        juicer.utils.Log.log_debug("Beginning remote->local sync: %s->%s" % (self.source, self.path))
        juicer.utils.save_url_as(self.source, dest_file)
        self.modified = True
        self.synced = True

    def __str__(self):
        return self.path if self.path else self.source
