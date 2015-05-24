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
import logging
import os
import progressbar
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
        if response.response_code == Constants.PULP_GET_OK:
            self.output.info("%s: %s OK" % (environment, hostname))
            return True
        else:
            self.output.info("%s: %s FAILED" % (environment, hostname))
            return False


class Repo(Pulp):
    """Pulp repository operations.

    :param connection: An instance of pulp.bindings.server.PulpConnection
    :type connection: pulp.bindings.server.PulpConnection

    :return: None
    """
    def __init__(self, connection):
        super(Repo, self).__init__(connection)

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
        """Delete a pulp repository.

        :param name: Repository name.
        :type name: str
        :param environment: Environment in which to delete repository.
        :type environment: str

        :return: True if repository deleted.
        :rtype: boolean
        """
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
        """List pulp repositories.

        :param environment: Environment repositories reside in.
        :type environment: str
        """
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
            rpm = juicer.types.RPM()
            repo_data = rpm.generate_repo_data(name, environment)
        elif 'docker' in repotype:
            docker = juicer.types.Docker()
            repo_data = docker.generate_repo_data(name, environment)
        elif 'iso' in repotype:
            iso = juicer.types.Iso()
            repo_data = iso.generate_repo_data(name, environment)

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

    def remove(self, name, environment, item_type, glob):
        repo_id = "{0}-{1}".format(name, environment)
        _pulp = pulp.bindings.repository.RepositoryUnitAPI(self.connection)
        criteria = {'type_ids': [item_type],
                    'filters': {'filename': {'$regex': glob}}}
        response = _pulp.remove(repo_id, type_ids=item_type, filters={'filename': {'$regex': glob}})
        if response.response_code == Constants.PULP_POST_ACCEPTED:
            self.output.info("call to delete %s from repo %s accepted" % (glob, name))
            return True
        else:
            self.output.error("call to delete %s from repo %s failed" % (glob, name))
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
            if response.response_code == Constants.PULP_PUT_OK:
                self.output.info("added %s to role %s in %s" % (login, name, environment))
                return True
            else:
                self.output.error("failed to add %s to role %s in %s" % (login, name, environment))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.NotFoundException:
            self.output.error("role %s does not exist in %s" % (name, environment))
            return False

    def create(self, name, environment, description):
        _pulp = pulp.bindings.auth.RoleAPI(self.connection)
        try:
            response = _pulp.create(
                {'role_id': name,
                 'display_name': name,
                 'description': description})
            if response.response_code == Constants.PULP_POST_CREATED:
                self.output.info("role %s created in %s" % (name, environment))
                return True
            else:
                self.output.error("failed to create role %s in %s" % (name, environment))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.ConflictException:
            self.output.error("role %s already exists in %s" % (name, environment))
            return False

    def delete(self, name, environment):
        _pulp = pulp.bindings.auth.RoleAPI(self.connection)
        try:
            response = _pulp.delete(name)
            if response.response_code == Constants.PULP_DELETE_OK:
                self.output.info("role %s deleted in %s" % (name, environment))
                return True
            else:
                self.output.error("failed to delete role %s in %s" % (name, environment))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.NotFoundException:
            self.output.error("role %s does not exist in %s" % (name, environment))
            return False

    def list(self, environment):
        _pulp = pulp.bindings.auth.RoleAPI(self.connection)
        response = _pulp.roles()
        if response.response_code == Constants.PULP_GET_OK:
            self.output.info(environment)
            for role in response.response_body:
                self.output.info("  {0}".format(role['display_name']))
            return True
        else:
            self.output.error("failed to list roles in %s" % environment)
            self.output.debug(response)
            return False

    def remove_user(self, name, environment, login):
        _pulp = pulp.bindings.auth.RoleAPI(self.connection)
        try:
            response = _pulp.remove_user(name, login)
            if response.response_code == Constants.PULP_PUT_OK:
                self.output.info("removed %s from role %s in %s" % (login, name, environment))
                return True
            else:
                self.output.error("failed to remove %s from role %s in %s" % (login, name, environment))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.NotFoundException:
            self.output.error("role %s does not exist in %s" % (name, environment))
            return False

    def show(self, name, environment):
        _pulp = pulp.bindings.auth.RoleAPI(self.connection)
        try:
            response = _pulp.role(name)
            if response.response_code == Constants.PULP_GET_OK:
                self.output.info(response.response_body)
                return True
            else:
                self.output.error("failed to show role %s in %s" % (name, environment))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.NotFoundException:
            self.output.error("role %s does not exist in %s" % (name, environment))
            return False


class Upload(Pulp):
    def __init__(self, connection):
        super(Upload, self).__init__(connection)
        self.environment = None
        self.name = None
        self.pbar = None

    def upload(self, path, repo, item_type, environment):
        self.name = os.path.basename(path)
        self.environment = environment
        repo_id = "{0}-{1}".format(repo, environment)
        size = os.path.getsize(path)

        if item_type == 'rpm':
            item = juicer.types.RPM(path)
        elif item_type == 'docker_image':
            item = juicer.types.Docker(path)
        elif item_type == 'iso':
            item = juicer.types.Iso(path)

        unit_key, unit_metadata = item.generate_upload_data()

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
        fd = open(path, 'rb')
        total_seeked = 0
        fd.seek(0)
        while total_seeked < size:
            chunk = fd.read(Constants.UPLOAD_AT_ONCE)
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
        fd.close()

        # Import upload. The import task returned will have a list of
        # spawned_tasks that we need to keep track of.
        import_task = self.import_upload(upload_id,
                                         repo_id,
                                         item_type,
                                         unit_key,
                                         unit_metadata)

        # Wait for the import to complete before we delete the upload
        # request. Use the first spawned task in the list of tasks.
        pulp_task = juicer.pulp.Task(self.connection)
        pulp_task.wait_for(import_task.spawned_tasks[0].task_id)

        # Finalize upload by cleaning up request on server.
        self.delete_upload(upload_id)

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
                                       unit_type,
                                       unit_key,
                                       unit_metadata)
        if response.response_code not in [Constants.PULP_POST_OK,
                                          Constants.PULP_POST_ACCEPTED]:
            self.output.error("Failed to import upload for %s" % self.name)
            raise SystemError("Failed to import upload for %s" % self.name)
        # This is an instance of pulp.bindings.responses.Task
        return response.response_body

    def delete_upload(self, upload_id):
        _pulp = pulp.bindings.upload.UploadAPI(self.connection)
        response = _pulp.delete_upload(upload_id)
        if response.response_code != Constants.PULP_DELETE_OK:
            self.output.error("Failed to clean up upload for %s" % self.name)
            raise SystemError("Failed to clean up upload for %s" % self.name)


class User(Pulp):
    def __init__(self, connection):
        super(User, self).__init__(connection)

    def create(self, login, password, environment, name=None, roles=None):
        _pulp = pulp.bindings.auth.UserAPI(self.connection)
        try:
            response = _pulp.create(login=login,
                                    password=password[0],
                                    name=name,
                                    roles=roles)
            if response.response_code == Constants.PULP_POST_CREATED:
                self.output.info("user %s created in %s" % (login, environment))
                return True
            else:
                self.output.error("failed to create user %s in %s" % (login, environment))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.ConflictException:
            self.output.error("user %s already exists in %s" % (login, environment))
            return False

    def delete(self, login, environment):
        _pulp = pulp.bindings.auth.UserAPI(self.connection)
        try:
            response = _pulp.delete(login)
            if response.response_code == Constants.PULP_DELETE_OK:
                self.output.info("user %s deleted in %s" % (login, environment))
                return True
            else:
                self.output.error("failed to delete user %s in %s" % (login, environment))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.NotFoundException:
            self.output.error("user %s does not exist in %s" % (login, environment))
            return False

    def list(self, environment):
        _pulp = pulp.bindings.auth.UserAPI(self.connection)
        response = _pulp.users()
        if response.response_code == Constants.PULP_GET_OK:
            self.output.info(environment)
            for user in response.response_body:
                self.output.info("  login: {0}, name: {1}, roles: {2}".format(
                    user['login'],
                    user['name'],
                    ', '.join(user['roles']) if user['roles'] else None))
            return True
        else:
            self.output.error("failed to list users in %s" % environment)
            self.output.debug(response)
            return False

    def show(self, login, environment):
        _pulp = pulp.bindings.auth.UserAPI(self.connection)
        try:
            response = _pulp.user(login)
            if response.response_code == Constants.PULP_GET_OK:
                user = response.response_body
                self.output.info(environment)
                self.output.info("  login: {0}".format(user['login']))
                self.output.info("  name: {0}".format(user['name']))
                self.output.info("  roles: {0}".format(', '.join(user['roles']) if user['roles'] else None))
                return True
            else:
                self.output.error("failed to show user %s in %s" % (login, environment))
                return False
        except pulp.bindings.exceptions.NotFoundException:
            self.output.error("user %s does not exist in %s" % (login, environment))
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

        try:
            response = _pulp.update(login, delta)
            if response.response_code == Constants.PULP_PUT_OK:
                self.output.info("user %s updated in %s" % (login, environment))
                return True
            else:
                self.output.error("failed to update user %s in %s" % (login, environment))
                self.output.debug(response)
                return False
        except pulp.bindings.exceptions.NotFoundException:
            self.output.error("user %s does not exist in %s" % (login, environment))
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
