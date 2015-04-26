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

from juicer.cart.Cart import Cart

class TestCart(TestCase):
    def setUp(self):
        pass

    def test_cart_without_provided_description(self):
        """A cart without items is empty"""
        cart = Cart('test-cart')
        self.assertEqual(cart.repo_items_hash, {})

    def test_cart_with_provided_description(self):
        """A cart with items is not empty"""
        cart = Cart('test-cart', [['test-repo', 'share/juicer/empty-0.1-1.noarch.rpm']])
        self.assertEqual(cart.repos(), ['test-repo'])
