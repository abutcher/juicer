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

import juicer.pulp


class TestPulp(TestCase):
    def setUp(self):
        pass

    def test_pulp_hello(self):
        """Verify pulp hello"""
        with nested(
                mock.patch('pulp.bindings.server_info'),
                mock.patch('juicer.common.Constants')) as (
                    server_info,
                    constants):

            constants.USER_CONFIG = './config'

            # Return value for the get_types() method call (serverInfoAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 200
            mock_pulp = mock.Mock(get_types=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).server_info.ServerInfoAPI
            server_info.ServerInfoAPI = mock.Mock(return_value=mock_pulp)
            _pulp = juicer.pulp.Pulp(None)
            responded = _pulp.hello(environment='re')

            # true for the case where connection made
            self.assertTrue(responded)

            mock_response.response_code = 400
            responded = _pulp.hello(environment='re')
            # true for the case where connection failed
            self.assertFalse(responded)
