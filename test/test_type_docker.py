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
import mock
import os.path

import juicer.types

class TestTypeDocker(TestCase):
    def setUp(self):
        self.docker_image = juicer.types.Docker(None)

    def test_upload_metadata(self):
        """Ensure docker image type upload data is sane"""
        with mock.patch('pulp_docker.common') as common:
            common.tarutils = mock.Mock(get_metadata=mock.MagicMock(return_value={'00000': None}))

            expected_unit_key = {'image_id': '00000'}
            expected_unit_metadata = {'00000': None}
            unit_key, unit_metadata = self.docker_image.generate_upload_data()
            self.assertEqual(expected_unit_key, unit_key)
            self.assertEqual(expected_unit_metadata, unit_metadata)
