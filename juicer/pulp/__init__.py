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

import logging
import os
import pulp.bindings.auth
import pulp.bindings.server_info
import pulp.bindings.repository
import pulp.bindings.exceptions
import pulp.bindings.responses
import pulp.bindings.tasks
import pulp.bindings.upload

from juicer.common import Constants
from juicer.config import Config
import juicer.types


class Pulp(object):
    def __init__(self, connection):
        self.connection = connection
        self.output = logging.getLogger('juicer')

    def hello(self, environment):
        config = Config()
        hostname = config.get(environment)['hostname']
        _pulp = pulp.bindings.server_info.ServerInfoAPI(self.connection)
        response = _pulp.get_types()
        stargs = {'environment': environment, 'hostname': hostname}
        if response.response_code == Constants.PULP_GET_OK:
            self.output.info("{environment}: {hostname} OK".format(**stargs))
            return True
        else:
            self.output.info("{environment}: {hostname} FAILED".format(**stargs))
            return False


class Repo(Pulp):
    """Pulp repository operations.

    :param connection: An instance of pulp.bindings.server.PulpConnection
    :type connection: pulp.bindings.server.PulpConnection

    :return: None
    """
    def __init__(self, connection):
        super(Repo, self).__init__(connection)

    def exists(self, name, environment):
        repo_id = "{name}-{environment}".format(name=name, environment=environment)
        _pulp = pulp.bindings.repository.RepositoryAPI(self.connection)
        try:
            _pulp.repository(repo_id)
            return True
        except pulp.bindings.exceptions.NotFoundException:
            return False

    def create(self, name, repotype, environment, checksumtype='sha256'):
        """Create a pulp repository.

        :param name: Repository name.
        :type name: str
        :param repotype: Repository type. One of ['rpm', 'docker', 'iso'].
        :type repotype: str
        :param environment: Environment in which to create the repository.
        :type environment: str

        :param checksumtype: Checksum type used for repository
                             metadata. One of ['sha', 'sha1', 'sha256']
        :type checksumtype: str

        :return: True if repository created.
        :rtype: boolean
        """
        _pulp = pulp.bindings.repository.RepositoryAPI(self.connection)

        if repotype == 'rpm':
            rpm = juicer.types.RPM()
            repo_data = rpm.generate_repo_data(name, environment, checksumtype)
        elif repotype == 'docker':
            docker = juicer.types.Docker()
            repo_data = docker.generate_repo_data(name, environment, checksumtype)
        elif repotype == 'iso':
            iso = juicer.types.Iso()
            repo_data = iso.generate_repo_data(name, environment, checksumtype)

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

            stargs = {'name': name, 'environment': environment}
            if response.response_code == Constants.PULP_POST_CREATED:
                self.output.info("Repo {name} created in {environment}".format(**stargs))
                return True
            else:
                self.output.error("Failed to create repo {name} in {environment}".format(**stargs))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.ConflictException:
            stargs = {'name': name, 'environment': environment}
            self.output.error("Repo {name} already exists in {environment}".format(**stargs))
            return False

    def delete(self, name, environment):
        """Delete a pulp repository.

        :param name: Repository name.
        :type name: str
        :param environment: Environment in which to delete repository.
        :type environment: str

        :return: True if repository deleted.
        :rtype: boolean
        """
        stargs = {'name': name, 'environment': environment}
        repo_id = "{name}-{environment}".format(**stargs)
        _pulp = pulp.bindings.repository.RepositoryAPI(self.connection)
        try:
            response = _pulp.delete(repo_id)
            if response.response_code == Constants.PULP_DELETE_ACCEPTED:
                self.output.info("Repo {name} deleted in {environment}".format(**stargs))
                return True
            else:
                self.output.error("Failed to delete repo {name} in {environment}".format(**stargs))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.NotFoundException:
            self.output.error("Repo {name} does not exist in {environment}".format(**stargs))
            return False

    def distributors(self, name, environment):
        stargs = {'name': name, 'environment': environment}
        repo_id = "{name}-{environment}".format(**stargs)
        _pulp = pulp.bindings.repository.RepositoryDistributorAPI(self.connection)
        try:
            response = _pulp.distributors(repo_id)
            if response.response_code == Constants.PULP_GET_OK:
                return response.response_body
            else:
                self.output.error("Failed to get distributors for repo {name} in {environment}".format(**stargs))
                self.output.debug(response)
                return []
        except pulp.bindings.exceptions.NotFoundException:
            self.output.error("Repo {name} does not exist in {environment}".format(**stargs))
            return []

    def list(self, environment):
        """List pulp repositories.

        :param environment: Environment repositories reside in.
        :type environment: str
        """
        _pulp = pulp.bindings.repository.RepositoryAPI(self.connection)
        response = _pulp.repositories()
        if response.response_code == Constants.PULP_GET_OK:
            self.output.info(environment)
            for repo in response.response_body:
                if "-{}".format(environment) in repo['id']:
                    self.output.info("  {}".format(repo['display_name']))
            return True
        else:
            self.output.error("Failed to list repos in {}".format(environment))
            self.output.debug(response)
            return False

    def publish(self, name, environment):
        _pulp = pulp.bindings.repository.RepositoryActionsAPI(self.connection)

        stargs = {'name': name, 'environment': environment}
        repo_id = "{name}-{environment}".format(**stargs)
        distributors = self.distributors(name, environment)

        published = []
        try:
            for distributor in distributors:
                response = _pulp.publish(repo_id, distributor['id'], {})
                if response.response_code == Constants.PULP_POST_ACCEPTED:
                    published.append(True)
                else:
                    self.output.debug("Failed to publish repo {name} in {environment}".format(**stargs))
                    self.output.debug(response)
                    published.append(False)
            return any(published)
        except pulp.bindings.exceptions.NotFoundException:
            self.output.error("Repo {name} does not exist in {environment}".format(**stargs))
            return False

    def remove(self, name, environment, item_type, glob):
        repo_id = "{name}-{environment}".format(name=name, environment=environment)
        _pulp = pulp.bindings.repository.RepositoryUnitAPI(self.connection)
        response = _pulp.remove(repo_id, type_ids=item_type, filters={'filename': {'$regex': glob}})
        stargs = {'glob': glob, 'name': name}
        if response.response_code == Constants.PULP_POST_ACCEPTED:
            self.output.info("Call to delete {glob} from repo {name} accepted".format(**stargs))
            return True
        else:
            self.output.error("Call to delete {glob} from repo {name} failed".format(**stargs))
            return False

    def show(self, name, environment, json=False):
        stargs = {'name': name, 'environment': environment}
        repo_id = "{name}-{environment}".format(**stargs)
        _pulp = pulp.bindings.repository.RepositoryAPI(self.connection)
        try:
            response = _pulp.repository(repo_id)
            if response.response_code == Constants.PULP_GET_OK:
                if json:
                    self.output.info(response.response_body)
                else:
                    repo = response.response_body
                    self.output.info(environment)
                    self.output.info("  name: {}".format(repo['display_name']))
                    if repo['content_unit_counts'] != {}:
                        for key in repo['content_unit_counts'].keys():
                            stargs = {'type': key, 'count': repo['content_unit_counts'][key]}
                            self.output.info("  {type}: {count}".format(**stargs))
                return True
            else:
                stargs = {'name': name, 'environment': environment}
                self.output.error("Failed to show repo {name} in {environment}".format(**stargs))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.NotFoundException:
            stargs = {'name': name, 'environment': environment}
            self.output.error("Repo {name} does not exist in {environment}".format(**stargs))
            return False


class Role(Pulp):
    """Pulp role operations.

    :param connection: An instance of pulp.bindings.server.PulpConnection
    :type connection: pulp.bindings.server.PulpConnection

    :return: None
    """
    def __init__(self, connection):
        super(Role, self).__init__(connection)

    def add_user(self, name, environment, login):
        _pulp = pulp.bindings.auth.RoleAPI(self.connection)
        try:
            response = _pulp.add_user(name, login)
            stargs = {'login': login, 'name': name, 'environment': environment}
            if response.response_code == Constants.PULP_PUT_OK:
                self.output.info("Added {login} to role {name} in {environment}".format(**stargs))
                return True
            else:
                self.output.error("Failed to add {login} to role {name} in {environment}".format(**stargs))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.NotFoundException:
            stargs = {'name': name, 'environment': environment}
            self.output.error("Role {name} does not exist in {environment}".format(**stargs))
            return False

    def create(self, name, environment, description):
        _pulp = pulp.bindings.auth.RoleAPI(self.connection)
        stargs = {'name': name, 'environment': environment}
        try:
            response = _pulp.create(
                {'role_id': name,
                 'display_name': name,
                 'description': description})
            if response.response_code == Constants.PULP_POST_CREATED:
                self.output.info("Role {name} created in {environment}".format(**stargs))
                return True
            else:
                self.output.error("Failed to create role {name} in {environment}".format(**stargs))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.ConflictException:
            self.output.error("Role {name} already exists in {environment}".format(**stargs))
            return False

    def delete(self, name, environment):
        _pulp = pulp.bindings.auth.RoleAPI(self.connection)
        stargs = {'name': name, 'environment': environment}
        try:
            response = _pulp.delete(name)
            if response.response_code == Constants.PULP_DELETE_OK:
                self.output.info("Role {name} deleted in {environment}".format(**stargs))
                return True
            else:
                self.output.error("Failed to delete role {name} in {environment}".format(**stargs))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.NotFoundException:
            self.output.error("Role {name} does not exist in {environment}".format(**stargs))
            return False

    def list(self, environment):
        _pulp = pulp.bindings.auth.RoleAPI(self.connection)
        response = _pulp.roles()
        if response.response_code == Constants.PULP_GET_OK:
            self.output.info(environment)
            for role in response.response_body:
                self.output.info("  {}".format(role['display_name']))
            return True
        else:
            self.output.error("Failed to list roles in {}".format(environment))
            self.output.debug(response)
            return False

    def remove_user(self, name, environment, login):
        _pulp = pulp.bindings.auth.RoleAPI(self.connection)
        try:
            response = _pulp.remove_user(name, login)
            stargs = {'login': login, 'name': name, 'environment': environment}
            if response.response_code == Constants.PULP_PUT_OK:
                self.output.info("Removed {login} from role {name} in {environment}".format(**stargs))
                return True
            else:
                self.output.error("Failed to remove {login} from role {name} in {environment}".format(**stargs))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.NotFoundException:
            stargs = {'name': name, 'environment': environment}
            self.output.error("Role {name} does not exist in {environment}".format(**stargs))
            return False

    def show(self, name, environment):
        _pulp = pulp.bindings.auth.RoleAPI(self.connection)
        stargs = {'name': name, 'environment': environment}
        try:
            response = _pulp.role(name)
            if response.response_code == Constants.PULP_GET_OK:
                self.output.info(response.response_body)
                return True
            else:
                self.output.error("Failed to show role {name} in {environment}".format(**stargs))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.NotFoundException:
            self.output.error("Role {name} does not exist in {environment}".format(**stargs))
            return False


class Upload(Pulp):
    def __init__(self, connection):
        super(Upload, self).__init__(connection)
        self.environment = None

    def upload(self, upload_id, path, repo, callback):
        """Upload an item to a repository.

        This method does not initialize, import, or delete uploads. It
        sends file chunks to pulp.
        """
        size = os.path.getsize(path)

        # Upload chunks w/ Constants.UPLOAD_AT_ONCE size.
        # Report progress using callback
        fd = open(path, 'rb')
        total_seeked = 0
        fd.seek(0)
        while total_seeked < size:
            last_offset = total_seeked
            chunk = fd.read(Constants.UPLOAD_AT_ONCE)
            total_seeked += len(chunk)
            stargs = {'bytes': len(chunk), 'total': total_seeked}
            self.output.debug("Seeked {bytes} data... (total seeked: {total})".format(**stargs))
            self.upload_segment(upload_id, last_offset, chunk)
            callback.update(min(callback.currval + len(chunk), callback.maxval))

    def initialize_upload(self):
        _pulp = pulp.bindings.upload.UploadAPI(self.connection)
        response = _pulp.initialize_upload()
        if response.response_code != Constants.PULP_POST_CREATED:
            raise SystemError("Failed to initialize upload:\n" + response.response_body)
        return response.response_body['upload_id']

    def upload_segment(self, upload_id, last_offset, chunk):
        _pulp = pulp.bindings.upload.UploadAPI(self.connection)
        response = _pulp.upload_segment(upload_id, last_offset, chunk)
        if response.response_code is not Constants.PULP_PUT_OK:
            raise SystemError("Failed to upload segment:\n" + response.response_body)

    def import_upload(self, upload_id, repo_id, unit_type, unit_key, unit_metadata):
        _pulp = pulp.bindings.upload.UploadAPI(self.connection)
        response = _pulp.import_upload(upload_id,
                                       repo_id,
                                       unit_type,
                                       unit_key,
                                       unit_metadata)
        if response.response_code not in [Constants.PULP_POST_OK,
                                          Constants.PULP_POST_ACCEPTED]:
            raise SystemError("Failed to import upload:\n" + response.response_body)
        # This is an instance of pulp.bindings.responses.Task
        return response.response_body

    def delete_upload(self, upload_id):
        _pulp = pulp.bindings.upload.UploadAPI(self.connection)
        response = _pulp.delete_upload(upload_id)
        if response.response_code != Constants.PULP_DELETE_OK:
            raise SystemError("Failed to clean up upload:\n" + response.response_body)


class User(Pulp):
    def __init__(self, connection):
        super(User, self).__init__(connection)

    def create(self, login, password, environment, name=None, roles=None):
        _pulp = pulp.bindings.auth.UserAPI(self.connection)
        stargs = {'login': login, 'environment': environment}
        try:
            response = _pulp.create(login=login,
                                    password=password[0],
                                    name=name,
                                    roles=roles)
            if response.response_code == Constants.PULP_POST_CREATED:
                self.output.info("User {login} created in {environment}".format(**stargs))
                return True
            else:
                self.output.error("Failed to create user {login} in {environment}".format(**stargs))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.ConflictException:
            self.output.error("Eser {login} already exists in {environment}".format(**stargs))
            return False

    def delete(self, login, environment):
        _pulp = pulp.bindings.auth.UserAPI(self.connection)
        stargs = {'login': login, 'environment': environment}
        try:
            response = _pulp.delete(login)
            if response.response_code == Constants.PULP_DELETE_OK:
                self.output.info("User {login} deleted in {environment}".format(**stargs))
                return True
            else:
                self.output.error("Failed to delete user {login} in {environment}".format(**stargs))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.NotFoundException:
            self.output.error("User {login} does not exist in {environment}".format(**stargs))
            return False

    def list(self, environment):
        _pulp = pulp.bindings.auth.UserAPI(self.connection)
        response = _pulp.users()
        if response.response_code == Constants.PULP_GET_OK:
            self.output.info(environment)
            for user in response.response_body:
                stargs = {'login': user['login'],
                          'name': user['name'],
                          'roles': ', '.join(user['roles']) if user['roles'] else None}
                self.output.info("  login: {login}, name: {name}, roles: {roles}".format(**stargs))
            return True
        else:
            self.output.error("Failed to list users in {}".format(environment))
            self.output.debug(response)
            return False

    def show(self, login, environment):
        _pulp = pulp.bindings.auth.UserAPI(self.connection)
        try:
            response = _pulp.user(login)
            if response.response_code == Constants.PULP_GET_OK:
                user = response.response_body
                self.output.info(environment)
                stargs = {'login': user['login'],
                          'name': user['name'],
                          'roles': ', '.join(user['roles']) if user['roles'] else None}
                self.output.info("  login: {login}".format(**stargs))
                self.output.info("  name: {name}".format(**stargs))
                self.output.info("  roles: {roles}".format(**stargs))
                return True
            else:
                stargs = {'login': login, 'environment': environment}
                self.output.error("Failed to show user {login} in {environment}".format(**stargs))
                return False
        except pulp.bindings.exceptions.NotFoundException:
            stargs = {'login': login, 'environment': environment}
            self.output.error("User {login} does not exist in {environment}".format(**stargs))
            return False

    def update(self, login, environment, password=None, name=None, roles=None):
        _pulp = pulp.bindings.auth.UserAPI(self.connection)

        delta = {}
        if password[0] is not None:
            delta['password'] = password[0]
        if name is not None:
            delta['name'] = name
        if roles is not None:
            delta['roles'] = roles

        stargs = {'login': login, 'environment': environment}

        try:
            response = _pulp.update(login, delta)
            if response.response_code == Constants.PULP_PUT_OK:
                self.output.info("User {login} updated in {environment}".format(**stargs))
                return True
            else:
                self.output.error("Failed to update user {login} in {environment}".format(**stargs))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.NotFoundException:
            self.output.error("User {login} does not exist in {environment}".format(**stargs))
            return False


class Task(Pulp):
    def __init__(self, connection):
        super(Task, self).__init__(connection)

    def get_task(self, task_id):
        _pulp = pulp.bindings.tasks.TasksAPI(self.connection)
        response = _pulp.get_task(task_id)
        if response.response_code == Constants.PULP_GET_OK:
            return response.response_body
        else:
            return None

    def wait_for(self, task_id):
        while not self.get_task(task_id).is_completed():
            pass
