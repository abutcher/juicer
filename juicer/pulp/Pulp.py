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

import logging
import pulp.bindings.server_info

from juicer.common import Constants
from juicer.config.Config import Config


class Pulp(object):
    def __init__(self, connection):
        self.connection = connection
        self.output = logging.getLogger('juicer')

    def hello(self, environment):
        config = Config()
        hostname = config.get(environment)['hostname']
        _pulp = pulp.bindings.server_info.ServerInfoAPI(self.connection)
        response = _pulp.get_types()
        if response.response_code == Constants.PULP_GET_OK:
            self.output.info("%s: %s OK" % (environment, hostname))
            return True
        else:
            self.output.info("%s: %s FAILED" % (environment, hostname))
            return False
