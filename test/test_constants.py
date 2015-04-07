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

from juicer.common import Constants as C

class TestConstants(TestCase):
    def setUp(self):
        pass

    def test_server_version(self):
        """The remote server version is what we expect"""
        # TODO: This should not be hard coded here. See also, the
        # Makefile variable 'PULPTAG' which refers to the pulp git
        # branch to use for testing
        self.assertEqual(C.EXPECTED_SERVER_VERSION, '2.6')

    def test_locations(self):
        """Verify pre-defined locations are what we expect"""
        home_path = os.getenv('HOME')
        self.assertEqual(C.CART_LOCATION, "%s/.config/juicer/carts" % home_path)
        self.assertEqual(C.USER_CONFIG, "%s/.config/juicer/config" % home_path)
        self.assertEqual(C.CONFIG_DIR, "%s/.config/juicer" % home_path)
        self.assertEqual(C.EXAMPLE_USER_CONFIG, '/usr/share/juicer/juicer.user.conf')
        self.assertEqual(C.EXAMPLE_SYSTEM_CONFIG, '/usr/share/juicer/juicer.conf')
