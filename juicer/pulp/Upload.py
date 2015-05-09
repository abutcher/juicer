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
import bitmath.integrations
import hashlib
import os
import progressbar
from pyrpm.rpm import RPM as PYRPM

import pulp.bindings.upload

from juicer.common import Constants
import juicer.pulp
from juicer.pulp.Pulp import Pulp


class Upload(Pulp):
    def __init__(self, connection):
        super(Upload, self).__init__(connection)
        self.environment = None
        self.name = None
        self.pbar = None

    def upload(self, path, repo, environment):
        self.name = os.path.basename(path)
        self.environment = environment
        repo_id = "{0}-{1}".format(repo, environment)
        size = os.path.getsize(path)
        unit_key, unit_metadata = self.generate_upload_data(path)

        # An array of widgets to design our progress bar.
        widgets = ['Uploading %s ' % self.name,
                   progressbar.Percentage(), ' ',
                   progressbar.Bar(marker=progressbar.RotatingMarker()), ' ',
                   progressbar.ETA(), ' ',
                   bitmath.integrations.BitmathFileTransferSpeed()]

        # Set up the progress bar.
        self.pbar = progressbar.ProgressBar(
            widgets=widgets,
            maxval=int(size)).start()

        # Initialize upload.
        upload_id = self.initialize_upload()

        # Upload chunks w/ Constants.UPLOAD_AT_ONCE size.
        rpm_fd = open(path, 'rb')
        total_seeked = 0
        rpm_fd.seek(0)
        while total_seeked < size:
            chunk = rpm_fd.read(Constants.UPLOAD_AT_ONCE)
            last_offset = total_seeked
            total_seeked += len(chunk)
            self.output.debug("Seeked %s data... (total seeked: %s)" %
                              (len(chunk), total_seeked))
            self.upload_segment(upload_id, last_offset, chunk)
            # Update the progress bar as we go.
            if total_seeked < self.pbar.maxval:
                self.pbar.update(int(total_seeked))

        # Finished with that.
        self.pbar.finish()

        # Import upload.
        self.import_upload(upload_id, repo_id, 'rpm', unit_key, unit_metadata)

        # Finalize upload by cleaning up request on server.
        self.delete_upload(upload_id)

        # Publish the repo.
        pulp_repo = juicer.pulp.Repo.Repo(self.connection)
        pulp_repo.publish(name=repo,
                          environment=environment)

        # FIN
        self.output.info("successfully uploaded %s" % self.name)

    def initialize_upload(self):
        _pulp = pulp.bindings.upload.UploadAPI(self.connection)
        response = _pulp.initialize_upload()
        if response.response_code == Constants.PULP_POST_CREATED:
            self.output.debug("Initialized upload process for %s" % self.name)
        else:
            raise SystemError("Failed to initialize upload process for %s" %
                              self.name)
        return response.response_body['upload_id']

    def upload_segment(self, upload_id, last_offset, chunk):
        _pulp = pulp.bindings.upload.UploadAPI(self.connection)
        response = _pulp.upload_segment(upload_id, last_offset, chunk)
        if response.response_code is not Constants.PULP_PUT_OK:
            self.output.error("Failed to upload %s" % self.name)
            raise SystemError("Failed to upload %s" % self.name)

    def import_upload(self, upload_id, repo_id, unit_type, unit_key, unit_metadata):
        _pulp = pulp.bindings.upload.UploadAPI(self.connection)
        response = _pulp.import_upload(upload_id,
                                       repo_id,
                                       'rpm',
                                       unit_key,
                                       unit_metadata)
        if response.response_code not in [Constants.PULP_POST_OK,
                                          Constants.PULP_POST_ACCEPTED]:
            self.output.error("Failed to import upload for %s" % self.name)
            raise SystemError("Failed to import upload for %s" % self.name)

    def delete_upload(self, upload_id):
        _pulp = pulp.bindings.upload.UploadAPI(self.connection)
        response = _pulp.delete_upload(upload_id)
        if response.response_code != Constants.PULP_DELETE_OK:
            self.output.error("Failed to clean up upload for %s" % self.name)
            raise SystemError("Failed to clean up upload for %s" % self.name)

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
