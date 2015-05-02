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
from juicer.pulp.PulpInterface import PulpInterface

import pulp.bindings.repository
import pulp.bindings.exceptions


class PulpRepo(PulpInterface):
    def __init__(self, connection):
        super(PulpRepo, self).__init__(connection)

    def create(self, name, environment, checksumtype='sha256'):
        repo_id = "{0}-{1}".format(name, environment)
        relative_url = "/{0}/{1}/".format(environment, name)
        checksumtype = checksumtype

        _pulp = pulp.bindings.repository.RepositoryAPI(self.connection)
        try:
            response = _pulp.create_and_configure(
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
                self.output.info("repo %s created in %s" % (name, environment))
                return True
            else:
                self.output.error("failed to create repo %s in %s" % (name, environment))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.ConflictException:
            self.output.error("repo %s already exists in %s" % (name, environment))
            return False

    def delete(self, name, environment):
        repo_id = "{0}-{1}".format(name, environment)
        _pulp = pulp.bindings.repository.RepositoryAPI(self.connection)
        try:
            response = _pulp.delete(repo_id)
            if response.response_code == Constants.PULP_DELETE_ACCEPTED:
                self.output.info("repo %s deleted in %s" % (name, environment))
                return True
            else:
                self.output.error("failed to delete repo %s in %s" % (name, environment))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.NotFoundException:
            self.output.error("repo %s does not exist in %s" % (name, environment))
            return False

    def list(self, environment):
        _pulp = pulp.bindings.repository.RepositoryAPI(self.connection)
        response = _pulp.repositories()
        if response.response_code == Constants.PULP_GET_OK:
            self.output.info(environment)
            for repo in response.response_body:
                if "-{0}".format(environment) in repo['id']:
                    self.output.info("  {0}".format(repo['display_name']))
            return True
        else:
            self.output.error("failed to list repos in %s" % environment)
            self.output.debug(response)
            return False

    def publish(self, name, environment):
        repo_id = "{0}-{1}".format(name, environment)
        _pulp = pulp.bindings.repository.RepositoryActionsAPI(self.connection)
        try:
            response = _pulp.publish(repo_id, 'yum_distributor', {})
            if response.response_code == Constants.PULP_POST_ACCEPTED:
                self.output.info("repo %s published in %s" % (name, environment))
                return True
            else:
                self.output.debug("failed to publish repo %s in %s" % (name, environment))
                self.output.debug(response)
                return False
        except pulp.bindings.exception.NotFoundException:
            self.output.error("repo %s does not exist in %s" % (name, environment))
            return False

    def show(self, name, environment, json=False):
        repo_id = "{0}-{1}".format(name, environment)
        _pulp = pulp.bindings.repository.RepositoryAPI(self.connection)
        try:
            response = _pulp.repository(repo_id)
            if response.response_code == Constants.PULP_GET_OK:
                if json:
                    self.output.info(response.response_body)
                else:
                    repo = response.response_body
                    self.output.info(environment)
                    self.output.info("  name: {0}".format(repo['display_name']))
                    self.output.info("  rpms: {0}".format(repo['content_unit_counts']['rpm']))
                return True
            else:
                self.output.error("failed to show repo %s in %s" % (name, environment))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.NotFoundException:
            self.output.error("repo %s does not exist in %s" % (name, environment))
            return False
