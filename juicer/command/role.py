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

from juicer.command import JuicerCommand
import juicer.pulp


def RoleAddCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    for environment in jc.args.environment:
        pulp_role = juicer.pulp.Role(jc.connections[environment])
        pulp_role.add_user(name=jc.args.role,
                           environment=environment,
                           login=jc.args.login)


def RoleListCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    for environment in jc.args.environment:
        pulp_role = juicer.pulp.Role(jc.connections[environment])
        pulp_role.list(environment=environment)
