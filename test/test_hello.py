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

from juicer.command.HelloCommand import HelloCommand
from juicer.parser.Parser import Parser


class TestHello(TestCase):
    def setUp(self):
        parser = Parser()
        self.args = parser.parser.parse_args(['hello'])

    def test_hello(self):
        """Verify that hello can be ran"""
        with mock.patch('pulp.bindings.server_info') as server_info:
            # Return value for the get_types() method call (serverInfoAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 200
            mock_pulp = mock.Mock(get_types=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).server_info.ServerInfoAPI
            server_info.ServerInfoAPI = mock.Mock(return_value=mock_pulp)
            hello = HelloCommand(self.args).run()

            # true for the case where connection made
            self.assertTrue(hello)

            mock_response.response_code = 400
            hello = HelloCommand(self.args).run()
            # true for the case where connection failed
            self.assertFalse(hello)
