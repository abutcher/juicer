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

import juicer.remotes

class TestRemotes(TestCase):
    def setUp(self):
        pass

    def test_classify_remotes(self):
        """Verify remote item classification"""
        resource_type = juicer.remotes.classify_resource_type("http://example.com/file.rpm")
        self.assertEqual(resource_type, juicer.remotes.REMOTE_PKG_TYPE)
        resource_type = juicer.remotes.classify_resource_type("http://example.com/stuff/")
        self.assertEqual(resource_type, juicer.remotes.REMOTE_INDEX_TYPE)
        resource_type = juicer.remotes.classify_resource_type("share/juicer/empty-0.1-1.noarch.rpm")
        self.assertEqual(resource_type, juicer.remotes.REMOTE_INPUT_FILE_TYPE)
        resource_type = juicer.remotes.classify_resource_type("potato")
        self.assertEqual(resource_type, None)
