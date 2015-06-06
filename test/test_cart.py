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
            constants.CART_LOCATION = './'
            constants.USER_CONFIG = './config'
            cart = juicer.cart.Cart('test-cart')
            self.assertEqual(cart.is_empty(), True)
            self.assertEqual(cart.repo_items_hash, {})

    def test_cart_with_provided_description(self):
        """A cart with items is not empty"""
        with mock.patch('juicer.common.Constants') as constants:
            constants.CART_LOCATION = './'
            constants.USER_CONFIG = './config'
            cart = juicer.cart.Cart('test-cart', [['test-repo', 'share/juicer/empty-0.1-1.noarch.rpm']])
            self.assertEqual(cart.repos(), ['test-repo'])
            self.assertEqual(cart.keys(), ['test-repo'])
            self.assertEqual(cart.is_empty(), False)
            self.assertIsInstance(str(cart), str)

    def test_cart_load(self):
        """A loaded cart is not empty"""
        with mock.patch('juicer.common.Constants') as constants:
            constants.CART_LOCATION = './'
            constants.USER_CONFIG = './config'
            cart = juicer.cart.Cart('cart', autoload=True)
            self.assertEqual(cart.repos(), ['test'])
            self.assertEqual(cart.is_empty(), False)
            self.assertEqual(cart.items()[0].name, 'empty-0.1-1.noarch.rpm')

    def test_cart_save_delete(self):
        """Cart can be saved and deleted"""
        with mock.patch('juicer.common.Constants') as constants:
            constants.CART_LOCATION = './'
            constants.USER_CONFIG = './config'
            cart = juicer.cart.Cart('test-cart', [['test-repo', 'share/juicer/empty-0.1-1.noarch.rpm']])
            cart.save()
            self.assertTrue(os.path.exists(cart.cart_file))
            cart.delete()
            self.assertFalse(os.path.exists(cart.cart_file))

    def test_cart_save_empty(self):
        """An empty cart will not be saved"""
        with mock.patch('juicer.common.Constants') as constants:
            constants.CART_LOCATION = './'
            constants.USER_CONFIG = './config'
            # A path that doesn't exist, like potato, should result in cart not being saved
            cart = juicer.cart.Cart('test-cart', [['test-repo', 'potato']])
            cart.save()
            self.assertFalse(os.path.exists(cart.cart_file))
        
    def test_cart_update(self):
        """Cart can be updated"""
        with mock.patch('juicer.common.Constants') as constants:
            constants.CART_LOCATION = './'
            constants.USER_CONFIG = './config'
            cart = juicer.cart.Cart('test-cart', [['test-repo', 'share/juicer/empty-0.1-1.noarch.rpm']])
            cart.save()
            self.assertTrue(os.path.exists(cart.cart_file))
            cart.update([['test-repo', 'share/juicer/empty-0.1-1.noarch.rpm']])
            self.assertEqual(cart.items()[0].name, 'empty-0.1-1.noarch.rpm')
            cart.delete()
            self.assertFalse(os.path.exists(cart.cart_file))
