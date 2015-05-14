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
import os.path
from pyrpm.rpm import RPM as PYRPM


class RPM(object):
    def __init__(self, path):
        self.path = path

    def generate_upload_data(self, checksumtype='sha256'):
        rpm = PYRPM(file(self.path))
        name = os.path.basename(self.path)
        unit_key = {
            'checksumtype': checksumtype,
            'checksum': getattr(hashlib, checksumtype)(self.path).hexdigest(),
            'epoch': str(rpm.header.epoch),
            'version': str(rpm.header.version),
            'release': str(rpm.header.release),
            'arch': str(rpm.header.architecture)
        }
        unit_metadata = {
            'vendor': None if str(rpm.header.vendor) == '' else str(rpm.header.vendor),
            'description': str(rpm.header.description),
            'license': str(rpm.header.license),
            'relativepath': name,
            'buildhost': str(rpm.header.build_host),
            'filename': name
        }
        return unit_key, unit_metadata
