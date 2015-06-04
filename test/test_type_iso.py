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
import os.path

import juicer.types

class TestTypeIso(TestCase):
    def setUp(self):
        self.iso = juicer.types.Iso('share/juicer/empty-0.1-1.noarch.rpm')

    def test_upload_metadata(self):
        """Ensure Iso type upload data is sane"""
        expected_unit_key = {'checksum': '9c9da0caa35238d0bc6f29c2bda2c385598b9e48f5903fd12393f47a03645aab',
                             'name': 'empty-0.1-1.noarch.rpm',
                             'size': 1468}
        expected_unit_metadata = {}
        unit_key, unit_metadata = self.iso.generate_upload_data()
        self.assertEqual(expected_unit_key, unit_key)
        self.assertEqual(expected_unit_metadata, unit_metadata)
