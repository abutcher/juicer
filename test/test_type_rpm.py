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

class TestTypeRPM(TestCase):
    def setUp(self):
        self.rpm = juicer.types.RPM('share/juicer/empty-0.1-1.noarch.rpm')

    def test_upload_metadata(self):
        """Ensure RPM type upload data is sane"""
        expected_unit_key = {'checksumtype': 'sha256',
                             'checksum': '320fda3ff8a6435e4eefae940e0823fbd14a93e9e2188d1a72bb40808ec04806',
                             'epoch': '0',
                             'version': '0.1',
                             'release': '1',
                             'arch': 'noarch'}
        expected_unit_metadata = {'vendor': None,
                                  'description': 'an empty package',
                                  'license': 'Public',
                                  'relativepath': 'empty-0.1-1.noarch.rpm',
                                  'filename': 'empty-0.1-1.noarch.rpm',
                                  'buildhost': 'localhost.localdomain'}
        unit_key, unit_metadata = self.rpm.generate_upload_data()
        self.assertEqual(expected_unit_key, unit_key)
        self.assertEqual(expected_unit_metadata, unit_metadata)
