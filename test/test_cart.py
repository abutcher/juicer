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
import json
import mock
import os

import juicer.cart
import pymongo


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
        with nested(
                mock.patch('juicer.common.Constants'),
                mock.patch('pymongo.MongoClient')) as (
                    constants,
                    MongoClient):

            # Override constants.
            constants.CART_LOCATION = './'
            constants.USER_CONFIG = './config'

            cart = juicer.cart.Cart('test-cart', [['test-repo', 'share/juicer/empty-0.1-1.noarch.rpm']])

            # We can save the cart and a file is created locally.
            cart.save()
            self.assertTrue(os.path.exists(cart.cart_file))
            # We can delete the cart and the file no longer exists.
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
        with nested(
                mock.patch('juicer.common.Constants'),
                mock.patch('pymongo.MongoClient')) as (
                    constants,
                    MongoClient):

            # Override constants.
            constants.CART_LOCATION = './'
            constants.USER_CONFIG = './config'

            cart = juicer.cart.Cart('test-cart', [['test-repo', 'share/juicer/empty-0.1-1.noarch.rpm']])
            cart.update([['test-repo', 'share/juicer/empty-0.1-1.noarch.rpm']])
            self.assertEqual(cart.items()[0].name, 'empty-0.1-1.noarch.rpm')
            cart.delete()
            self.assertFalse(os.path.exists(cart.cart_file))

    def test_cart_pull(self):
        """Cart can be pulled"""
        with nested(
                mock.patch('juicer.common.Constants'),
                mock.patch('pymongo.MongoClient')) as (
                    constants,
                    MongoClient):

            # Override constants.
            constants.CART_LOCATION = './'
            constants.USER_CONFIG = './config'

            test_cart_body = {
                "_id": "potato",
                "repos_items": {
	            "test": [
	                "share/juicer/empty-0.1-1.noarch.rpm"
	            ]
                }
            }

            # MongoClient().carts.__getitem__().find_one()
            mock_find_one = mock.MagicMock(find_one=mock.MagicMock(return_value=test_cart_body))
            mock_mongo = mock.MagicMock(carts=mock.MagicMock(__getitem__=mock.MagicMock(name="shit",return_value=mock_find_one)))

            # pymongo.MongoClient
            MongoClient.return_value = mock_mongo

            cart = juicer.cart.Cart('potato')
            # Do an initial pull
            cart.pull()
            self.assertTrue(os.path.exists(cart.cart_file))
            # Pull to overwrite existing file
            cart.pull()
            self.assertTrue(os.path.exists(cart.cart_file))
            # Delete cart file
            cart.delete()
            self.assertFalse(os.path.exists(cart.cart_file))

            # MongoClient().carts.__getitem__().find_one()
            mock_find_one = mock.MagicMock(find_one=mock.MagicMock(return_value=None))
            mock_mongo = mock.MagicMock(carts=mock.MagicMock(__getitem__=mock.MagicMock(return_value=mock_find_one)))

            # pymongo.MongoClient()
            MongoClient.return_value = mock_mongo

            # We can't pull a cart that doesn't exist on the remote
            cart = juicer.cart.Cart('potato')
            cart.pull()
            self.assertFalse(os.path.exists(cart.cart_file))
