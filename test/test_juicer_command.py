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
import os

import juicer.command
from juicer.parser.Parser import Parser as Parser


class TestCart(TestCase):
    def setUp(self):
        pass

    def test_command(self):
        """Can instantiate a JuicerCommand"""
        with nested (
                mock.patch('juicer.common.Constants'),
                mock.patch('pulp.bindings.server')) as (
                    constants,
                    server):
            constants.USER_CONFIG = './config'
            server.PulpConnection = mock.MagicMock()
            command = juicer.command.JuicerCommand(None)

    def test_command_cart_list(self):
        """Carts can be listed via cart command"""
        with nested (
                mock.patch('juicer.common.Constants'),
                mock.patch('pulp.bindings.server')) as (
                    constants,
                    server):
            constants.USER_CONFIG = './config'
            constants.CART_LOCATION = './'
            server.PulpConnection = mock.MagicMock()

            parser = Parser()
            args = parser.parser.parse_args(['cart', 'list'])
            args.cmd(args)

            args = parser.parser.parse_args(['cart', 'list', 'ca*.json'])
            args.cmd(args)
