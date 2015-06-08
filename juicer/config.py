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
            raise SystemExit("No config file was found at '{config}'".format(
                config=juicer.common.Constants.USER_CONFIG))

        configs.append(juicer.common.Constants.USER_CONFIG)
        config.read(configs)
        return config

    def get(self, section=None):
        return self.config[section]

    def keys(self):
        return self.config.keys()

    def environments(self):
        environments = []
        start_in = self.start_in()
        environments.append(start_in)

        current = start_in
        while 'promotes_to' in self.get(current).keys():
            current = self.get(current)['promotes_to']
            environments.append(current)
        return environments

    def start_in(self):
        return self.get(self.keys()[0])['start_in']

    def test(self):
        """
        confirm the provided config has the required attributes and
        has a valid promotion path
        """
        required_keys = set(['username',
                             'password',
                             'hostname',
                             'port',
                             'verify_ssl',
                             'ca_path',
                             'cert_filename',
                             'start_in'])

        for environment in self.config.keys():
            cfg = self.config.get(environment)

            # ensure required keys are present in each section
            if not required_keys.issubset(set(cfg.keys())):
                raise SystemExit("Error reading juicer config file '{config}':"
                                 "\nConfig does not contain the following required values: {missing}"
                                 "\n\nFor additional information see 'man 5 juicer.conf'".format(
                                     config=juicer.common.Constants.USER_CONFIG,
                                     missing=', '.join(list(required_keys - set(cfg.keys())))))

            # ensure promotion path exists
            if 'promotes_to' in cfg and cfg['promotes_to'] not in self.config.keys():
                raise SystemExit("Error reading juicer config file '{config}':"
                                 "\nSection '{environment}' promotes to '{promotes_to}', but '{promotes_to}' is not a config section"
                                 "\n\nFor additional information see 'man 5 juicer.conf'".format(
                                     config=juicer.common.Constants.USER_CONFIG,
                                     environment=environment,
                                     promotes_to=cfg['promotes_to']))
