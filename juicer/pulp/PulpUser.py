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
from pulp.bindings.auth import UserAPI
from pulp.bindings.exceptions import NotFoundException


class PulpUser(object):
    def __init__(self, connection):
        self.connection = connection

    def create(self, login, password, environment, name=None, roles=None):
        pulp = UserAPI(self.connection)
        if self.exists(login):
            Log.log_info("user %s already exists in %s" % (login, environment))
        else:
            response = pulp.create(login=login,
                                   password=password[0],
                                   name=name,
                                   roles=roles)
            if response.response_code == Constants.PULP_POST_CREATED:
                Log.log_info("user %s created in %s" % (login, environment))
            else:
                Log.log_error("failed to create user %s in %s" % (login, environment))
                Log.log_debug(response)

    def delete(self, login, environment):
        pulp = UserAPI(self.connection)
        response = pulp.delete(login)
        if response.response_code == Constants.PULP_DELETE_OK:
            Log.log_info("user %s deleted in %s" % (login, environment))
        else:
            Log.log_error("failed to delete user %s in %s" % (login, environment))
            Log.log_debug(response)

    def exists(self, login):
        exists = False
        pulp = UserAPI(self.connection)
        try:
            response = pulp.user(login)
            if response.response_code == Constants.PULP_GET_OK:
                exists = True
        except NotFoundException:
            pass
        return exists

    def list(self, environment):
        pulp = UserAPI(self.connection)
        response = pulp.users()
        if response.response_code == Constants.PULP_GET_OK:
            Log.log_info(response.response_body)
        else:
            Log.log_error("failed to list users in %s" % environment)
            Log.log_debug(response)

    def show(self, login, environment):
        pulp = UserAPI(self.connection)
        try:
            response = pulp.user(login)
            Log.log_info(response.response_body)
        except NotFoundException:
            Log.log_error("failed to show user %s in %s" % (login, environment))
            Log.log_debug(response)

    def update(self, login, environment, password=None, name=None, roles=None):
        pulp = UserAPI(self.connection)

        delta = {}
        if password[0] is not None:
            delta['password'] = password[0]
        if name is not None:
            delta['name'] = name
        if roles is not None:
            delta['roles'] = roles

        response = pulp.update(login, delta)
        if response.response_code == Constants.PULP_PUT_OK:
            Log.log_info("user %s updated in %s" % (login, environment))
        else:
            Log.log_error("failed to update user %s in %s" % (login, environment))
            Log.log_debug(response)
