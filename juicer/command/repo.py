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


def RepoCreateCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    for environment in jc.args.environment:
        pulp_repo = juicer.pulp.Repo(jc.connections[environment])
        pulp_repo.create(name=jc.args.repo,
                         repotype=jc.args.repotype,
                         environment=environment,
                         checksumtype=jc.args.checksum_type)
        pulp_repo.publish(name=jc.args.repo,
                          environment=environment)


def RepoDeleteCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    for environment in jc.args.environment:
        pulp_repo = juicer.pulp.Repo(jc.connections[environment])
        pulp_repo.delete(name=jc.args.repo,
                         environment=environment)


def RepoListCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    for environment in jc.args.environment:
        pulp_repo = juicer.pulp.Repo(jc.connections[environment])
        pulp_repo.list(environment=environment)


def RepoPublishCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    for environment in jc.args.environment:
        pulp_repo = juicer.pulp.Repo(jc.connections[environment])
        pulp_repo.publish(name=jc.args.repo,
                          environment=environment)


def RepoShowCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    for environment in jc.args.environment:
        for repo in jc.args.repo:
            pulp_repo = juicer.pulp.Repo(jc.connections[environment])
            pulp_repo.show(name=repo,
                           environment=environment,
                           json=jc.args.json)
