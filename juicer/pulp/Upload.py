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
from juicer.pulp.Pulp import Pulp
from juicer.pulp.Repo import Repo
from pyrpm.rpm import RPM as PYRPM
from pulp.bindings.upload import UploadAPI
import os


class Upload(Pulp):
    def __init__(self, connection):
        super(Upload, self).__init__(connection)

    def upload(self, path, repo, environment):
        pulp = UploadAPI(self.connection)
        unit_key, unit_metadata = self.generate_upload_data(path)
        name = os.path.basename(path)
        repo_id = "{0}-{1}".format(repo, environment)

        ################################################################
        # Initialize upload
        ################################################################
        response = pulp.initialize_upload()
        if response.response_code == Constants.PULP_POST_CREATED:
            self.output.debug("Initialized upload process for %s" % name)
        else:
            raise SystemError("Failed to initialize upload process for %s" %
                              name)
        upload_id = response.response_body['upload_id']

        ################################################################
        # Upload chunks w/ Constants.UPLOAD_AT_ONCE size
        ################################################################
        size = os.path.getsize(path)
        rpm_fd = open(path, 'rb')
        total_seeked = 0
        rpm_fd.seek(0)

        while total_seeked < size:
            chunk = rpm_fd.read(Constants.UPLOAD_AT_ONCE)
            last_offset = total_seeked
            total_seeked += len(chunk)

            self.output.notice("Seeked %s data... (total seeked: %s)" %
                               (len(chunk), total_seeked))

            response = pulp.upload_segment(upload_id, last_offset, chunk)
            if response.response_code is not Constants.PULP_PUT_OK:
                self.output.error("Failed to upload %s" % name)
                raise SystemError("Failed to upload %s" % name)

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
            self.output.error("Failed to import upload for %s" % name)
            raise SystemError("Failed to import upload for %s" % name)

        self.output.debug("RPM upload %s complete" % name)

        ################################################################
        # Finalize upload by cleaning up request on server
        ################################################################
        response = pulp.delete_upload(upload_id)
        if response.response_code != Constants.PULP_DELETE_OK:
            self.output.error("Failed to clean up upload for %s" % name)
            raise SystemError("Failed to clean up upload for %s" % name)

        ################################################################
        # Publish the repo
        ################################################################
        pulp_repo = Repo(self.connection)
        pulp_repo.publish(name=repo,
                          environment=environment)

        ################################################################
        # FIN
        ################################################################
        self.output.info("successfully uploaded %s" % name)

    def generate_upload_data(self, path, checksumtype='sha256'):
        rpm = PYRPM(file(path))
        name = os.path.basename(path)
        unit_key = {
            'checksumtype': checksumtype,
            'checksum': getattr(hashlib, checksumtype)(path).hexdigest(),
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
