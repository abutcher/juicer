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

from juicer.juicer.JuicerCommand import JuicerCommand
from juicer.common import Constants
from juicer.log import Log


class RepoPublishCommand(JuicerCommand):
    def __init__(self, args):
        super(RepoPublishCommand, self).__init__(args)


    def run(self):
        from pulp.bindings.repository import RepositoryActionsAPI
        
        for environment in self.args.environment:
            repo_id = "{0}-{1}".format(self.args.repo, environment)
            display_name = self.args.repo

            pulp = RepositoryActionsAPI(self.connections[environment])
            response = pulp.publish(repo_id, 'yum_distributor', {})

            if response.response_code == Constants.PULP_POST_ACCEPTED:
                Log.log_info("%s published in %s", display_name, environment)
            else:
                Log.log_info("failed to publish %s in %s", display_name, environment)
                Log.log_debug(response)
