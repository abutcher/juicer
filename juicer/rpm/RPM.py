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
from juicer.common import Constants
from juicer.log import Log
import magic
import os.path
from pyrpm.rpm import RPM as PYRPM
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

    def generate_upload_data(self, checksumtype='sha256'):
        rpm = PYRPM(file(self.path))
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
            'relativepath': self.name,
            'buildhost': str(rpm.header.build_host),
            'filename': self.name
        }
        return unit_key, unit_metadata

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

    def upload(self, repo_id, environment, connection):
        from pulp.bindings.upload import UploadAPI

        if not self.synced:
            self.sync()

        pulp = UploadAPI(connection)
        unit_key, unit_metadata = self.generate_upload_data()

        ################################################################
        # Initialize upload
        ################################################################
        response = pulp.initialize_upload()
        if response.response_code == Constants.PULP_POST_CREATED:
            Log.log_debug("Initialized upload process for %s" % self.name)
        else:
            raise SystemError("Failed to initialize upload process for %s" %
                              self.name)
        upload_id = response.response_body['upload_id']

        ################################################################
        # Upload chunks w/ Constants.UPLOAD_AT_ONCE size
        ################################################################
        size = os.path.getsize(self.path)
        rpm_fd = open(self.path, 'rb')
        total_seeked = 0
        rpm_fd.seek(0)

        while total_seeked < size:
            chunk = rpm_fd.read(Constants.UPLOAD_AT_ONCE)
            last_offset = total_seeked
            total_seeked += len(chunk)

            Log.log_notice("Seeked %s data... (total seeked: %s)" %
                           (len(chunk), total_seeked))

            response = pulp.upload_segment(upload_id, last_offset, chunk)
            if response.response_code is not Constants.PULP_PUT_OK:
                Log.log_debug("Failed to upload %s" % self.name)
                raise SystemError("Failed to upload %s" % self.name)

        ################################################################
        # Import upload
        ################################################################
        response = pulp.import_upload(upload_id,
                                      repo_id,
                                      'rpm',
                                      unit_key,
                                      unit_metadata)
        if response.response_code not in [Constants.PULP_POST_OK,
                                          Constants.PULP_POST_ACCEPTED]:
            Log.log_error("Failed to import upload for %s" % self.name)
            raise SystemError("Failed to import upload for %s" % self.name)

        Log.log_debug("RPM upload %s complete" % self.name)

        ################################################################
        # Finalize upload by cleaning up request on server
        ################################################################
        response = pulp.delete_upload(upload_id)
        if response.response_code != Constants.PULP_DELETE_OK:
            Log.log_error("Failed to clean up upload for %s" % self.name)
            raise SystemError("Failed to clean up upload for %s" % self.name)

        ################################################################
        # FIN
        ################################################################
        Log.log_info("successfully uploaded %s" % self.name)
