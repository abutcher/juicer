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

from juicer.rpm.RPM import RPM

class TestRPM(TestCase):
    def setUp(self):
        self.rpm = RPM('share/juicer/empty-0.1-1.noarch.rpm')

    def test_rpm_local(self):
        """Local rpm registers as local"""
        self.assertEqual(self.rpm.path, os.path.abspath('share/juicer/empty-0.1-1.noarch.rpm'))
        self.assertEqual(self.rpm.synced, True)

    def test_rpm_upload_data(self):
        """Upload data can be properly divined"""
        self.assertEqual(self.rpm.upload_data(), {'unit_key': {'package_basename': 'empty-0.1-1.noarch.rpm', 'epoch': 0, 'version': u'0.1', 'name': u'empty', 'checksum_type': 'sha256', 'release': u'1', 'checksum': '1e66cefbecee3da340ff740a3ac95a72fcab151e7bd8ee80360beab33796ce5d', 'arch': u'noarch', 'size': 1468}, 'unit_metadata': {'relativepath': 'empty-0.1-1.noarch.rpm', 'vendor': '', 'description': u'an empty package', 'license': u'Public', 'filename': 'empty-0.1-1.noarch.rpm'}})

    def test_rpm_verify(self):
        """A valid rpm is valid"""
        self.assertEqual(self.rpm.verify(), True)
