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

import juicer.cart
import juicer.pulp
from juicer.command import JuicerCommand


def RPMDeleteCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    for environment in jc.args.environment:
        pulp_repo = juicer.pulp.Repo(jc.connections[environment])
        for repo, item in jc.args.r:
            pulp_repo.remove(name=repo,
                             environment=environment,
                             item_type='rpm',
                             glob=item)
            pulp_repo.publish(repo, 'rpm', environment)


def RPMUploadCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    for environment in jc.args.environment:
        jc.output.info("Starting upload for {} environment".format(environment))
        cart = juicer.cart.Cart('upload-cart', jc.args.r)
        cart.upload_items(environment, jc.connections[environment])
