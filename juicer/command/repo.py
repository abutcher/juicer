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


class RepoCreateCommand(JuicerCommand):
    def __init__(self, args):
        super(RepoCreateCommand, self).__init__(args)

    def run(self):
        for environment in self.args.environment:
            pulp_repo = juicer.pulp.Repo(self.connections[environment])
            pulp_repo.create(name=self.args.repo,
                             repotype=self.args.repotype,
                             environment=environment,
                             checksumtype=self.args.checksum_type)
            pulp_repo.publish(name=self.args.repo,
                              environment=environment)


class RepoDeleteCommand(JuicerCommand):
    def __init__(self, args):
        super(RepoDeleteCommand, self).__init__(args)

    def run(self):
        for environment in self.args.environment:
            pulp_repo = juicer.pulp.Repo(self.connections[environment])
            pulp_repo.delete(name=self.args.repo,
                             environment=environment)


class RepoListCommand(JuicerCommand):
    def __init__(self, args):
        super(RepoListCommand, self).__init__(args)

    def run(self):
        for environment in self.args.environment:
            pulp_repo = juicer.pulp.Repo(self.connections[environment])
            pulp_repo.list(environment=environment)


class RepoPublishCommand(JuicerCommand):
    def __init__(self, args):
        super(RepoPublishCommand, self).__init__(args)

    def run(self):
        for environment in self.args.environment:
            pulp_repo = juicer.pulp.Repo(self.connections[environment])
            pulp_repo.publish(name=self.args.repo,
                              environment=environment)


class RepoShowCommand(JuicerCommand):
    def __init__(self, args):
        super(RepoShowCommand, self).__init__(args)

    def run(self):
        for environment in self.args.environment:
            for repo in self.args.repo:
                pulp_repo = juicer.pulp.Repo(self.connections[environment])
                pulp_repo.show(name=repo,
                               environment=environment,
                               json=self.args.json)
