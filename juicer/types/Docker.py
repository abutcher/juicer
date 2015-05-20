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
from pulp_docker.common import tarutils


class Docker(object):
    def __init__(self, path=None):
        self.path = path

    def generate_repo_data(self, name, environment, checksumtype='sha256'):
        repo_id = "{0}-{1}".format(name, environment)
        relative_url = "/{0}/{1}/".format(environment, name)
        repo_data = {}
        repo_data['id'] = repo_id
        repo_data['display_name'] = name
        repo_data['description'] = repo_id
        repo_data['notes'] = {'_repo-type': 'docker-repo'}
        repo_data['importer_type_id'] = 'docker_importer'
        repo_data['importer_config'] = {}
        repo_data['distributors'] = [{'distributor_id': 'docker_web_distributor_name_cli',
                                      'distributor_type_id': 'docker_distributor_web',
                                      'distributor_config': {},
                                      'auto_publish': True,
                                      'relative_path': relative_url},
                                     {'distributor_id': 'docker_export_distributor_name_cli',
                                      'distributor_type_id': 'docker_distributor_export',
                                      'distributor_config': {},
                                      'auto_publish': True,
                                      'relative_path': relative_url
                                     }]
        return repo_data

    def generate_upload_data(self, checksumtype='sha256'):
        unit_key = {}
        unit_metadata = tarutils.get_metadata(self.path)
        print unit_metadata
        return unit_key, unit_metadata
