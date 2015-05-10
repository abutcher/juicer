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

import fnmatch
import os.path

from juicer.command.JuicerCommand import JuicerCommand
from juicer.common import Constants
from juicer.cart.Cart import Cart


class CartListCommand(JuicerCommand):
    def __init__(self, args):
        super(CartListCommand, self).__init__(args)

    def run(self):
        carts = []
        for glob in self.args.cart_glob:
            # Translate cart names into cart file names
            if not glob.endswith('.json'):
                search_glob = glob + ".json"
            else:
                search_glob = glob

            for cart in self._find_pattern(Constants.CART_LOCATION, search_glob):
                cart_name = cart.split('/')[-1].replace('.json', '')
                carts.append(cart_name)
        for cart in sorted(carts):
            self.output.info("{0}".format(cart))

    def _find_pattern(self, search_base, pattern):
        # Stolen from http://rosettacode.org/wiki/Walk_a_directory/Recursively#Python
        if (not os.path.isdir(search_base)) and os.path.exists(search_base):
            # Adapt the algorithm to gracefully handle non-directory search paths
            yield search_base
        else:
            for root, dirs, files in os.walk(search_base):
                for filename in fnmatch.filter(files, pattern):
                    yield os.path.join(root, filename)
