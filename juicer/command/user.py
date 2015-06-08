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


def UserCreateCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    for environment in jc.args.environment:
        pulp_user = juicer.pulp.User(jc.connections[environment])
        pulp_user.create(login=jc.args.login,
                         password=jc.args.password,
                         environment=environment,
                         name=jc.args.name,
                         roles=jc.args.roles)


def UserDeleteCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    for environment in jc.args.environment:
        pulp_user = juicer.pulp.User(jc.connections[environment])
        pulp_user.delete(login=jc.args.login,
                         environment=environment)


def UserListCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    for environment in jc.args.environment:
        pulp_user = juicer.pulp.User(jc.connections[environment])
        pulp_user.list(environment=environment)


def UserShowCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    for environment in jc.args.environment:
        pulp_user = juicer.pulp.User(jc.connections[environment])
        pulp_user.show(login=jc.args.login,
                       environment=environment)


def UserUpdateCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    for environment in jc.args.environment:
        pulp_user = juicer.pulp.User(jc.connections[environment])
        pulp_user.update(login=jc.args.login,
                         password=jc.args.password,
                         environment=environment,
                         name=jc.args.name,
                         roles=jc.args.roles)
