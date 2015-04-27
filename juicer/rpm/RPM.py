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
import re
import rpm


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

    def upload_data(self):
        return self._generate_rpm_data(self.path)

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
        unit_key, unit_metadata = self.upload_data()

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

    def _generate_rpm_data(self, rpm_filename, user_metadata=None):
        """
        For the given RPM, analyzes its metadata to generate the appropriate unit
        key and metadata fields, returning both to the caller.

        :param rpm_filename: full path to the RPM to analyze
        :type  rpm_filename: str
        :param user_metadata: user supplied metadata about the unit. This is optional.
        :type  user_metadata: dict

        :return: tuple of unit key and unit metadata for the RPM
        :rtype:  tuple
        """

        # Expected metadata fields:
        # "vendor", "description", "buildhost", "license", "vendor", "requires", "provides", "relativepath", "filename"
        #
        # Expected unit key fields:
        # "name", "epoch", "version", "release", "arch", "checksumtype", "checksum"

        unit_key = dict()
        metadata = dict()

        # Read the RPM header attributes for use later
        ts = rpm.TransactionSet()
        ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES)
        fd = os.open(rpm_filename, os.O_RDONLY)
        try:
            headers = ts.hdrFromFdno(fd)
            os.close(fd)
        except rpm.error:
            # Raised if the headers cannot be read
            os.close(fd)
            raise

        # -- Unit Key -----------------------
        # Checksum
        if user_metadata and user_metadata.get('checksum_type'):
            user_checksum_type = user_metadata.get('checksum_type')
            unit_key['checksumtype'] = user_checksum_type
        else:
            unit_key['checksumtype'] = 'sha256'
            unit_key['checksum'] = getattr(hashlib, unit_key['checksumtype'])(rpm_filename).hexdigest()

        # Name, Version, Release, Epoch
        for k in ['name', 'version', 'release', 'epoch']:
            unit_key[k] = headers[k]

        #   Epoch munging
        if unit_key['epoch'] is None:
            unit_key['epoch'] = str(0)
        else:
            unit_key['epoch'] = str(unit_key['epoch'])

        # Arch
        if headers['sourcepackage']:
            if RPMTAG_NOSOURCE in headers.keys():
                unit_key['arch'] = 'nosrc'
            else:
                unit_key['arch'] = 'src'
        else:
            unit_key['arch'] = headers['arch']

        # -- Unit Metadata ------------------

        # construct filename from metadata (BZ #1101168)
        if headers[rpm.RPMTAG_SOURCEPACKAGE]:
            rpm_basefilename = "%s-%s-%s.src.rpm" % (headers['name'],
                                                     headers['version'],
                                                     headers['release'])
        else:
            rpm_basefilename = "%s-%s-%s.%s.rpm" % (headers['name'],
                                                    headers['version'],
                                                    headers['release'],
                                                    headers['arch'])

        metadata['relativepath'] = rpm_basefilename
        metadata['filename'] = rpm_basefilename

        # This format is, and has always been, incorrect. As of the new yum importer, the
        # plugin will generate these from the XML snippet because the API into RPM headers
        # is atrocious. This is the end game for this functionality anyway, moving all of
        # that metadata derivation into the plugin, so this is just a first step.
        # I'm leaving these in and commented to show how not to do it.
        # metadata['requires'] = [(r,) for r in headers['requires']]
        # metadata['provides'] = [(p,) for p in headers['provides']]

        metadata['buildhost'] = headers['buildhost']
        metadata['license'] = headers['license']
        metadata['vendor'] = headers['vendor']
        metadata['description'] = headers['description']
        return unit_key, metadata
