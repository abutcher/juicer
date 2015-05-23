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

import juicer.cart


class TestCart(TestCase):
    def setUp(self):
        pass

    def test_cart_without_provided_description(self):
        """A cart without items is empty"""
        with mock.patch('juicer.common.Constants') as constants:
            constants.USER_CONFIG = './config'
            cart = juicer.cart.Cart('test-cart')
            self.assertEqual(cart.is_empty(), True)
            self.assertEqual(cart.repo_items_hash, {})

    def test_cart_with_provided_description(self):
        """A cart with items is not empty"""
        with mock.patch('juicer.common.Constants') as constants:
            constants.USER_CONFIG = './config'
            cart = juicer.cart.Cart('test-cart', [['test-repo', 'share/juicer/empty-0.1-1.noarch.rpm']])
            self.assertEqual(cart.repos(), ['test-repo'])
            self.assertEqual(cart.keys(), ['test-repo'])
            self.assertEqual(cart.is_empty(), False)
            self.assertIsInstance(str(cart), str)
