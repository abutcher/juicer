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
        self.local_rpm = RPM('share/juicer/empty-0.1-1.noarch.rpm')
        self.remote_rpm = RPM('http://somesite.com/some-rpm-0.0.1-1.noarch.rpm')

    def test_local_rpm(self):
        """Local rpm registers as local"""
        self.assertEqual(self.local_rpm.path, os.path.abspath('share/juicer/empty-0.1-1.noarch.rpm'))
        self.assertTrue(self.local_rpm.synced)

    def test_local_rpm_upload_data(self):
        """Upload data can be properly divined"""
        unit_key, unit_metadata = self.local_rpm.upload_data()
        self.assertEqual(unit_metadata['filename'], 'empty-0.1-1.noarch.rpm')

    def test_local_rpm_verify(self):
        """A valid, local rpm is valid"""
        self.assertTrue(self.local_rpm.verify())

    def test_remote_rpm(self):
        """Remote rpm registers as remote"""
        self.assertEqual(self.remote_rpm.path, None)
        self.assertFalse(self.remote_rpm.synced)

    def test_remote_rpm_verify(self):
        """A valid(?), remote rpm is valid"""
        self.assertTrue(self.remote_rpm.verify())
