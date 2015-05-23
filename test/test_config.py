# Copyright (C) 2015 SEE AUTHORS FILE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from . import TestCase, unittest
from contextlib import nested
import os

import mock
import juicer.config

# When the config file is read in and parsed it will turn into a dict
# like this
serialized_config = {
    "qa": {
        "ca_path": "/home/testuser/certs/pulp.crt",
        "cert_filename": "/home/testuser/certs/client.crt",
        "hostname": "testhost.qa.example.com",
        "password": "testpass",
        "port": "443",
        "start_in": "re",
        "username": "testuser",
        "verify_ssl": "False"
    },
    "re": {
        "ca_path": "/home/testuser/certs/pulp.crt",
        "cert_filename": "/home/testuser/certs/client.crt",
        "hostname": "testhost.re.example.com",
        "password": "testpass",
        "port": "443",
        "promotes_to": "qa",
        "start_in": "re",
        "username": "testuser",
        "verify_ssl": "False"
    }
}

class TestConfig(TestCase):
    def test_initialize_config_good(self):
        """Configs can be read in properly"""
        # the config class looks for the cert elsewhere, let's
        # override that by mocking the value of the USER_CONFIG
        # variable to a known cart config and then creating the config
        # object.
        with mock.patch('juicer.common.Constants') as constants:
            constants.USER_CONFIG = './config'
            c = juicer.config.Config()

            # We've read in the config, now let's verify it has what
            # we expect. The sample config file has two environments
            # defined, 'qa', and 're'
            self.assertIn('qa', c.config)
            self.assertIn('re', c.config)

            re = c.get('re')
            qa = c.get('qa')

            self.assertEqual(re, serialized_config['re'])
            self.assertEqual(qa, serialized_config['qa'])

            # Check one last time that every key in the config object
            # matches the expected configs
            self.assertEqual(c.keys(), serialized_config.keys())

    def test_initialize_config_bad(self):
        """The config object isn't created if the config file doesn't exist"""
        # patch the constant to point to a non-existant cart
        with mock.patch('juicer.common.Constants') as constants:
            constants.USER_CONFIG = './doesnt-exist-config'
            with self.assertRaises(SystemError):
                c = juicer.config.Config()

    def test_get_missing_config_section(self):
        """KeyError raises if an invalid config section is requested"""
        with mock.patch('juicer.common.Constants') as constants:
            constants.USER_CONFIG = './config'
            c = juicer.config.Config()

            with self.assertRaises(KeyError):
                bad = c.get('badbadbad')
