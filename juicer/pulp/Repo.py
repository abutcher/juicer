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
from juicer.pulp.Pulp import Pulp
import juicer.types

import pulp.bindings.repository
import pulp.bindings.exceptions


class Repo(Pulp):
    def __init__(self, connection):
        super(Repo, self).__init__(connection)

    def create(self, name, repotype, environment, checksumtype='sha256'):
        _pulp = pulp.bindings.repository.RepositoryAPI(self.connection)

        if repotype == 'rpm':
            rpm = juicer.types.RPM.RPM()
            repo_data = rpm.generate_repo_data(name, environment, checksumtype)
        elif repotype == 'docker':
            docker = juicer.types.Docker.Docker()
            repo_data = docker.generate_repo_data(name, environment, checksumtype)

        try:
            response = _pulp.create_and_configure(
                id=repo_data['id'],
                display_name=repo_data['display_name'],
                description=repo_data['description'],
                notes=repo_data['notes'],
                importer_type_id=repo_data['importer_type_id'],
                importer_config=repo_data['importer_config'],
                distributors=repo_data['distributors']
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

    def publish(self, name, repotype, environment):
        _pulp = pulp.bindings.repository.RepositoryActionsAPI(self.connection)

        if repotype == 'rpm':
            rpm = juicer.types.RPM.RPM()
            repo_data = rpm.generate_repo_data(name, environment)
        elif repotype == 'docker':
            docker = juicer.types.Docker.Docker()
            repo_data = docker.generate_repo_data(name, environment)

        published = []
        try:
            for distributor in repo_data['distributors']:
                response = _pulp.publish(repo_data['id'], distributor['distributor_id'], {})
                if response.response_code == Constants.PULP_POST_ACCEPTED:
                    published.append(True)
                else:
                    self.output.debug("failed to publish repo %s in %s" % (name, environment))
                    self.output.debug(response)
                    published.append(False)
            if any(published):
                self.output.info("repo %s published in %s" % (name, environment))
            return any(published)
        except pulp.bindings.exceptions.NotFoundException:
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
                    if repo['content_unit_counts']:
                        self.output.info("  rpms: {0}".format(repo['content_unit_counts']['rpm']))
                    else:
                        self.output.info("  rpms: {0}".format(0))
                return True
            else:
                self.output.error("failed to show repo %s in %s" % (name, environment))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.NotFoundException:
            self.output.error("repo %s does not exist in %s" % (name, environment))
            return False
