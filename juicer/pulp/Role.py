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

import pulp.bindings.auth
import pulp.bindings.exceptions


class Role(Pulp):
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
                 'description': desription})
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
