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

import pulp.bindings.auth
import pulp.bindings.exceptions


class PulpUser(PulpInterface):
    def __init__(self, connection):
        super(PulpUser, self).__init__(connection)

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
