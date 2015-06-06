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

from juicer.common import Constants
from juicer.command import JuicerCommand
import juicer.cart


class CartCreateCommand(JuicerCommand):  # pragma: no cover
    def __init__(self, args):
        super(CartCreateCommand, self).__init__(args)

    def run(self):
        juicer.cart.Cart(self.args.cartname, self.args.r, autosave=True)


class CartDeleteCommand(JuicerCommand):  # pragma: no cover
    def __init__(self, args):
        super(CartDeleteCommand, self).__init__(args)

    def run(self):
        cart = juicer.cart.Cart(self.args.cartname)
        cart.delete()
        self.output.info("Successfully deleted cart {}".format(cart.name))


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
            self.output.info("{}".format(cart))

    def _find_pattern(self, search_base, pattern):
        # Stolen from http://rosettacode.org/wiki/Walk_a_directory/Recursively#Python
        if (not os.path.isdir(search_base)) and os.path.exists(search_base):
            # Adapt the algorithm to gracefully handle non-directory search paths
            yield search_base
        else:
            for root, dirs, files in os.walk(search_base):
                for filename in fnmatch.filter(files, pattern):
                    yield os.path.join(root, filename)


class CartPullCommand(JuicerCommand):  # pragma: no cover
    def __init__(self, args):
        super(CartPullCommand, self).__init__(args)

    def run(self):
        cart = juicer.cart.Cart(self.args.cartname, autoload=False, autosave=False, autosync=False)
        cart.pull()


class CartPushCommand(JuicerCommand):  # pragma: no cover
    def __init__(self, args):
        super(CartPushCommand, self).__init__(args)

    def run(self):
        cart = juicer.cart.Cart(self.args.cartname, autoload=True, autosave=True, autosync=False)
        for environment in self.args.environment:
            cart.upload_items(environment, self.connections[environment], self.args.force)


class CartShowCommand(JuicerCommand):  # pragma: no cover
    def __init__(self, args):
        super(CartShowCommand, self).__init__(args)

    def run(self):
        cart = juicer.cart.Cart(self.args.cartname, autoload=True)
        self.output.info(str(cart))


class CartUpdateCommand(JuicerCommand):  # pragma: no cover
    def __init__(self, args):
        super(CartUpdateCommand, self).__init__(args)

    def run(self):
        cart = juicer.cart.Cart(self.args.cartname, autoload=True)
        cart.update(self.args.r)
