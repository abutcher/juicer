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

from juicer.command.JuicerCommand import JuicerCommand
from juicer.interface.PulpRepo import PulpRepo


class RepoCreateCommand(JuicerCommand):
    def __init__(self, args):
        super(RepoCreateCommand, self).__init__(args)

    def run(self):
        for environment in self.args.environment:
            pulp_repo = PulpRepo(self.connections[environment])
            pulp_repo.create(name=self.args.repo,
                             environment=environment,
                             checksumtype=self.args.checksum_type)
            pulp_repo.publish(name=self.args.repo,
                              environment=environment)
