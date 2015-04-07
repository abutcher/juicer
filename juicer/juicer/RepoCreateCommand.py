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


class RepoCreateCommand(JuicerCommand):
    def __init__(self, args):
        super(RepoCreateCommand, self).__init__(args)


    def run(self):
        from pulp.bindings.repository import RepositoryAPI
        from pulp.bindings.repository import RepositoryActionsAPI
        
        for environment in self.args.environment:
            repo_id = "{0}-{1}".format(self.args.repo, environment)
            display_name = self.args.repo
            relative_url = "/{0}/{1}/".format(environment, self.args.repo)
            checksum_type = self.args.checksum_type

            pulp = RepositoryAPI(self.connections[environment])
            response = pulp.create_and_configure(
                id=repo_id,
                display_name=display_name,
                description=repo_id,
                notes={'_repo-type': 'rpm-repo'},
                importer_type_id='yum_importer',
                importer_config={},
                distributors=[{ 'distributor_id': 'yum_distributor',
                                'distributor_type_id': 'yum_distributor',
                                'distributor_config': {
                                    'relative_url': relative_url,
                                    'http': True,
                                    'https': True,
                                    'checksum_type': checksum_type
                                },
                                'auto_publish': True,
                                'relative_path': relative_url
                        }]
            )

            if response.response_code == Constants.PULP_POST_CREATED:
                Log.log_info("%s created in %s", display_name, environment)
            else:
                Log.log_info("failed to create %s in %s", display_name, environment)
                Log.log_debug(response)

            pulp = RepositoryActionsAPI(self.connections[environment])
            response = pulp.publish(repo_id, 'yum_distributor', {})

            if response.response_code == Constants.PULP_POST_ACCEPTED:
                Log.log_info("%s published in %s", display_name, environment)
            else:
                Log.log_info("failed to publish %s in %s", display_name, environment)
                Log.log_debug(response)
