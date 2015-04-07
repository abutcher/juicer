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

from juicer.config.Config import Config
from juicer.common import Constants
from juicer.log import Log
from pulp.bindings.exceptions import *
from pulp.bindings.server import PulpConnection


class JuicerCommand(object):
    def __init__(self, args):
        self.args = args
        self.config = Config()

        self.connections = {}
        for environment in self.config.keys():
            cfg = self.config.get(environment)
            self.connections[environment] = PulpConnection(
                cfg['hostname'],
                int(cfg['port']),
                username = cfg['username'],
                password = cfg['password'],
                cert_filename = cfg['cert_filename'],
                verify_ssl = False,
                ca_path = cfg['ca_path'])


    def upload(self):
        pass


    def cart_push(self):
        pass


    def publish(self):
        pass


    def cart_create(self):
        pass


    def cart_update(self):
        pass


    def cart_show(self):
        pass


    def cart_pull(self):
        pass


    def cart_list(self):
        pass

    def delete_rpms(self):
        pass


    def publish_repo(self, repo=None, environments=None):
        from pulp.bindings.repository import RepositoryActionsAPI

        for environment in environments:
            pulp = RepositoryActionsAPI(self.connections[environment])
            repo_id = "{0}-{1}".format(repo, environment)
            distributor_id = 'yum_distributor'
            try:
                response = pulp.publish(repo_id, distributor_id, None)
                if response.status_code != Constants.PULP_POST_ACCEPTED:
                    Log.log_info("%s published in %s", repo, environment)
                else:
                    Log.log_info("failed to publish %s in %s", repo, environment)
            except NotFoundException:
                Log.log_info("%s not found in %s", repo, environment)


    def cart_delete(self):
        pass
