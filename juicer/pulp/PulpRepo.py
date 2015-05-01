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
from pulp.bindings.repository import RepositoryAPI
from pulp.bindings.repository import RepositoryActionsAPI
from pulp.bindings.exceptions import ConflictException
from pulp.bindings.exceptions import NotFoundException


class PulpRepo(object):
    def __init__(self, connection):
        self.connection = connection

    def create(self, name, environment, checksumtype='sha256'):
        repo_id = "{0}-{1}".format(name, environment)
        relative_url = "/{0}/{1}/".format(environment, name)
        checksumtype = checksumtype

        pulp = RepositoryAPI(self.connection)
        try:
            response = pulp.create_and_configure(
                id=repo_id,
                display_name=name,
                description=repo_id,
                notes={'_repo-type': 'rpm-repo'},
                importer_type_id='yum_importer',
                importer_config={},
                distributors=[{'distributor_id': 'yum_distributor',
                               'distributor_type_id': 'yum_distributor',
                               'distributor_config': {
                                   'relative_url': relative_url,
                                   'http': True,
                                   'https': True,
                                   'checksum_type': checksumtype
                               },
                               'auto_publish': True,
                               'relative_path': relative_url
                           }]
            )

            if response.response_code == Constants.PULP_POST_CREATED:
                Log.log_info("repo %s created in %s", name, environment)
            else:
                Log.log_error("failed to create repo %s in %s", name, environment)
                Log.log_debug(response)
        except ConflictException:
            Log.log_error("repo %s already exists in %s", name, environment)

    def delete(self, name, environment):
        repo_id = "{0}-{1}".format(name, environment)
        pulp = RepositoryAPI(self.connection)
        try:
            response = pulp.delete(repo_id)
            if response.response_code == Constants.PULP_DELETE_ACCEPTED:
                Log.log_info("repo %s deleted in %s", name, environment)
            else:
                Log.log_error("failed to delete repo %s in %s", name, environment)
                Log.log_debug(response)
        except NotFoundException:
            Log.log_error("repo %s does not exist in %s", name, environment)

    def list(self, environment):
        pulp = RepositoryAPI(self.connection)
        response = pulp.repositories()
        if response.response_code == Constants.PULP_GET_OK:
            Log.log_info(environment)
            for repo in response.response_body:
                if "-{0}".format(environment) in repo['id']:
                    Log.log_info("  {0}".format(repo['display_name']))
        else:
            Log.log_error("failed to list repos in %s" % environment)
            Log.log_debug(response)

    def publish(self, name, environment):
        repo_id = "{0}-{1}".format(name, environment)
        pulp = RepositoryActionsAPI(self.connection)
        try:
            response = pulp.publish(repo_id, 'yum_distributor', {})
            if response.response_code == Constants.PULP_POST_ACCEPTED:
                Log.log_debug("repo %s published in %s", name, environment)
            else:
                Log.log_debug("failed to publish repo %s in %s", name, environment)
                Log.log_debug(response)
        except NotFoundException:
            Log.log_error("repo %s does not exist in %s", name, environment)

    def show(self, name, environment, json=False):
        repo_id = "{0}-{1}".format(name, environment)
        pulp = RepositoryAPI(self.connection)
        try:
            response = pulp.repository(repo_id)
            if response.response_code == Constants.PULP_GET_OK:
                if json:
                    Log.log_info(response.response_body)
                else:
                    repo = response.response_body
                    Log.log_info(environment)
                    Log.log_info("  name: {0}".format(repo['display_name']))
                    Log.log_info("  rpms: {0}".format(repo['content_unit_counts']['rpm']))
            else:
                Log.log_error("failed to show repo %s in %s", name, environment)
                Log.log_debug(response)
        except NotFoundException:
            Log.log_error("repo %s does not exist in %s", name, environment)
