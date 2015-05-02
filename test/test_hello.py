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

    @mock.patch('juicer.common.Constants')
    @mock.patch('pulp.bindings.responses.Response')
    @mock.patch('pulp.bindings.server_info.ServerInfoAPI')
    def test_hello(self, mock_Constants, mock_Response, mock_ServerInfoAPI):
        """Verify that hello can be ran"""
        mock_Constants.USER_CONFIG = './config'
        mock_Response.response_code = 200
        mock_Response.response_body = '[{}]'
        mock_ServerInfoAPI.types.return_value = mock_Response
        hello = HelloCommand(self.args).run()
