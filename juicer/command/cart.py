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


def CartCreateCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    juicer.cart.Cart(jc.args.cartname, jc.args.r, autosave=True)


def CartDeleteCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    cart = juicer.cart.Cart(jc.args.cartname)
    cart.delete(local=jc.args.local,
                remote=jc.args.remote)


def CartListCommand(args):
    jc = JuicerCommand(args)

    carts = []
    for glob in jc.args.cart_glob:
        # Translate cart names into cart file names
        if not glob.endswith('.json'):
            search_glob = glob + ".json"
        else:
            search_glob = glob

        for cart in _find_pattern(Constants.CART_LOCATION, search_glob):
            cart_name = cart.split('/')[-1].replace('.json', '')
            carts.append(cart_name)
    for cart in sorted(carts):
        jc.output.info("{}".format(cart))


def _find_pattern(search_base, pattern):
    # Stolen from http://rosettacode.org/wiki/Walk_a_directory/Recursively#Python
    if (not os.path.isdir(search_base)) and os.path.exists(search_base):
        # Adapt the algorithm to gracefully handle non-directory search paths
        yield search_base  # pragma: no cover
    else:
        for root, dirs, files in os.walk(search_base):
            for filename in fnmatch.filter(files, pattern):
                yield os.path.join(root, filename)


def CartPullCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    cart = juicer.cart.Cart(jc.args.cartname, autoload=False, autosave=False, autosync=False)
    cart.pull()


def CartPushCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    cart = juicer.cart.Cart(jc.args.cartname, autoload=True, autosave=True, autosync=False)
    for environment in jc.args.environment:
        cart.upload_items(environment, jc.connections[environment], jc.args.force)


def CartShowCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    cart = juicer.cart.Cart(jc.args.cartname, autoload=True)
    jc.output.info(str(cart))


def CartUpdateCommand(args):  # pragma: no cover
    jc = JuicerCommand(args)

    cart = juicer.cart.Cart(jc.args.cartname, autoload=True)
    cart.update(jc.args.r)
