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
import pulp_docker.common.tarutils
from pyrpm.rpm import RPM as PYRPM


class Iso(object):
    def __init__(self, path=None):
        self.path = path
        self.pattern = r'(.+)\.(.+)'

    def generate_repo_data(self, name, environment, checksumtype='sha256'):
        repo_id = "{0}-{1}".format(name, environment)
        relative_url = "/{0}/{1}/".format(environment, name)
        repo_data = {'id': repo_id,
                     'display_name': name,
                     'description': repo_id,
                     'notes': {'_repo-type': 'iso-repo'},
                     'importer_type_id': 'iso_importer',
                     'importer_config': {},
                     'distributors': [{'distributor_id': 'iso_distributor',
                                       'distributor_type_id': 'iso_distributor',
                                       'distributor_config': {
                                           'http': True,
                                           'https': True,
                                           'serve_http': True,
                                       },
                                       'auto_publish': True,
                                       'relative_path': relative_url}]}
        return repo_data

    def generate_upload_data(self, checksumtype='sha256'):
        name = os.path.basename(self.path)
        size = os.path.getsize(self.path)
        checksum = getattr(hashlib, checksumtype)(open(self.path, 'rb').read()).hexdigest()
        unit_key = {
            'name': name,
            'checksum': checksum,
            'size': size,
        }
        unit_metadata = {}
        return unit_key, unit_metadata


class Docker(object):
    def __init__(self, path=None):
        self.path = path
        self.pattern = r'(.+)\.tar'

    def generate_repo_data(self, name, environment, checksumtype='sha256'):
        repo_id = "{0}-{1}".format(name, environment)
        relative_url = "/{0}/{1}/".format(environment, name)
        repo_data = {'id': repo_id,
                     'display_name': name,
                     'description': repo_id,
                     'notes': {'_repo-type': 'docker-repo'},
                     'importer_type_id': 'docker_importer',
                     'importer_config': {},
                     'distributors': [{'distributor_id': 'docker_web_distributor_name_cli',
                                       'distributor_type_id': 'docker_distributor_web',
                                       'distributor_config': {},
                                       'auto_publish': True,
                                       'relative_path': relative_url},
                                      {'distributor_id': 'docker_export_distributor_name_cli',
                                       'distributor_type_id': 'docker_distributor_export',
                                       'distributor_config': {},
                                       'auto_publish': True,
                                       'relative_path': relative_url}]}
        return repo_data

    def generate_upload_data(self, checksumtype='sha256'):
        unit_metadata = pulp_docker.common.tarutils.get_metadata(self.path)
        unit_key = {'image_id': unit_metadata.keys()[0]}
        return unit_key, unit_metadata


class RPM(object):
    def __init__(self, path=None):
        self.path = path
        self.pattern = r'(.+)\.rpm'

    def generate_repo_data(self, name, environment, checksumtype='sha256'):
        repo_id = "{0}-{1}".format(name, environment)
        relative_url = "/{0}/{1}/".format(environment, name)
        repo_data = {'id': repo_id,
                     'display_name': name,
                     'description': repo_id,
                     'notes': {'_repo-type': 'rpm-repo'},
                     'importer_type_id': 'yum_importer',
                     'importer_config': {},
                     'distributors': [{'distributor_id': 'yum_distributor',
                                       'distributor_type_id': 'yum_distributor',
                                       'distributor_config': {
                                           'relative_url': relative_url,
                                           'http': True,
                                           'https': True,
                                           'checksum_type': checksumtype
                                       },
                                       'auto_publish': True,
                                       'relative_path': relative_url}]}
        return repo_data

    def generate_upload_data(self, checksumtype='sha256'):
        rpm = PYRPM(file(self.path))
        name = os.path.basename(self.path)
        checksum = getattr(hashlib, checksumtype)(open(self.path, 'rb').read()).hexdigest()
        unit_key = {
            'checksumtype': checksumtype,
            'checksum': checksum,
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
