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

from juicer.config import Config
from pulp.bindings.server import PulpConnection
import logging


class JuicerCommand(object):
    def __init__(self, args):
        self.args = args
        self.config = Config()
        self.output = logging.getLogger('juicer')

        self.connections = {}
        for environment in self.config.keys():
            cfg = self.config.get(environment)
            self.connections[environment] = PulpConnection(
                cfg['hostname'],
                int(cfg['port']),
                username=cfg['username'],
                password=cfg['password'],
                cert_filename=cfg['cert_filename'],
                verify_ssl=False,
                ca_path=cfg['ca_path'])
