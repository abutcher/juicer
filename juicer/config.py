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

import ConfigParser
import juicer.common.Constants
import os


class Config(object):
    def __init__(self):
        cfg = self.read()
        self.config = {}
        for section in cfg.sections():
            self.config[section] = dict(cfg.items(section))

    def read(self):
        config = ConfigParser.SafeConfigParser()
        configs = []

        if not os.path.exists(juicer.common.Constants.USER_CONFIG):
            raise SystemError("No configuration file found: %s" % juicer.common.Constants.USER_CONFIG)

        configs.append(juicer.common.Constants.USER_CONFIG)
        config.read(configs)
        return config

    def get(self, section=None):
        return self.config[section]

    def keys(self):
        return self.config.keys()
