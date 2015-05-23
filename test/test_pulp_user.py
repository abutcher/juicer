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
from juicer.parser.Parser import Parser

import pulp.bindings.exceptions


class TestUser(TestCase):
    def setUp(self):
        pass

    def test_pulp_user_create(self):
        """Verify pulp user create"""
        with mock.patch('pulp.bindings.auth') as auth:
            # Return value for the create() method call (UserAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 201
            mock_pulp = mock.Mock(create=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).auth.UserAPI
            auth.UserAPI = mock.Mock(return_value=mock_pulp)

            pulp_user = juicer.pulp.User(None)
            created = pulp_user.create(login='test-user',
                                       password='sw33tp@55w3rd',
                                       name='Test User',
                                       environment='re',
                                       roles=['super-users'])
            # true for the case where user created
            self.assertTrue(created)

            mock_response.response_code = 400
            created = pulp_user.create(login='test-user',
                                       password='sw33tp@55w3rd',
                                       name='Test User',
                                       environment='re',
                                       roles=['super-users'])
            # true for the case where user not created
            self.assertFalse(created)

            mock_pulp = mock.Mock(create=mock.MagicMock(side_effect=pulp.bindings.exceptions.ConflictException({'_href': 'oh no'})))
            auth.UserAPI = mock.Mock(return_value=mock_pulp)
            pulp_user = juicer.pulp.User(None)
            # false for the case where user not created due to a conflict
            created = pulp_user.create(login='test-user',
                                       password='sw33tp@55w3rd',
                                       name='Test User',
                                       environment='re',
                                       roles=['super-users'])
            self.assertFalse(created)

    def test_pulp_user_delete(self):
        """Verify pulp user delete"""
        with mock.patch('pulp.bindings.auth') as auth:
            # Return value for the delete() method call (UserAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 200
            mock_pulp = mock.Mock(delete=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).auth.UserAPI
            auth.UserAPI = mock.Mock(return_value=mock_pulp)
            pulp_user = juicer.pulp.User(None)
            deleted = pulp_user.delete(login='test-user',
                                       environment='re')
            # true for the case where user deleted
            self.assertTrue(deleted)

            mock_response.response_code = 400
            deleted = pulp_user.delete(login='test-user',
                                       environment='re')
            # false for the case where user not deleted
            self.assertFalse(deleted)

            mock_pulp = mock.Mock(delete=mock.MagicMock(side_effect=pulp.bindings.exceptions.NotFoundException({'_href': 'oh no'})))
            auth.UserAPI = mock.Mock(return_value=mock_pulp)
            # false for the case where user not deleted because it didn't exist
            deleted = pulp_user.delete(login='test-user',
                                       environment='re')

            self.assertFalse(deleted)

    def test_pulp_user_list(self):
        """Verify pulp user list"""
        with mock.patch('pulp.bindings.auth') as auth:
            # Return value for the users() method call (UserAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 200
            mock_response.response_body = [{'login': 'test-user',
                                            'name': 'Test User',
                                            'roles': ['super-users']}]
            mock_pulp = mock.Mock(users=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).auth.UserAPI
            auth.UserAPI = mock.Mock(return_value=mock_pulp)
            pulp_user = juicer.pulp.User(None)
            listed = pulp_user.list(environment='re')
            # true for the case where user listed
            self.assertTrue(listed)

            mock_response.response_code = 400
            listed = pulp_user.list(environment='re')
            # false for the case where user not listed
            self.assertFalse(listed)

    def test_pulp_user_show(self):
        """Verify pulp user show"""
        with mock.patch('pulp.bindings.auth') as auth:
            # Return value for the user() method call (UserAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 200
            mock_response.response_body = {'login': 'test-user',
                                           'name': 'Test User',
                                           'roles': ['super-users']}
            mock_pulp = mock.Mock(user=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).auth.UserAPI
            auth.UserAPI = mock.Mock(return_value=mock_pulp)
            pulp_user = juicer.pulp.User(None)
            shown = pulp_user.show(login='test-user',
                                   environment='re')
            # true for the case where user shown
            self.assertTrue(shown)

            mock_response.response_code = 400
            shown = pulp_user.show(login='test-user',
                                   environment='re')
            # false for the case where user not shown
            self.assertFalse(shown)

            mock_pulp = mock.Mock(user=mock.MagicMock(side_effect=pulp.bindings.exceptions.NotFoundException({'_href': 'oh no'})))
            auth.UserAPI = mock.Mock(return_value=mock_pulp)
            pulp_user = juicer.pulp.User(None)
            # false for the case where user not shown because it didn't exist
            shown = pulp_user.show(login='test-user',
                                   environment='re')
            self.assertFalse(shown)

    def test_pulp_user_update(self):
        """Verify pulp user update"""
        with mock.patch('pulp.bindings.auth') as auth:
            # Return value for the update() method call (UserAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 200
            mock_pulp = mock.Mock(update=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).auth.UserAPI
            auth.UserAPI = mock.Mock(return_value=mock_pulp)
            pulp_user = juicer.pulp.User(None)
            updated = pulp_user.update(login='test-user',
                                       password='sw337',
                                       name='New Name',
                                       environment='re',
                                       roles=['super-users'])
            # true for the case where user updated
            self.assertTrue(updated)

            mock_response.response_code = 400
            updated = pulp_user.update(login='test-user',
                                       password='sw337',
                                       name='New Name',
                                       environment='re',
                                       roles=['super-users'])
            # false for the case where user not updated
            self.assertFalse(updated)

            mock_pulp = mock.Mock(update=mock.MagicMock(side_effect=pulp.bindings.exceptions.NotFoundException({'_href': 'oh no'})))
            auth.UserAPI = mock.Mock(return_value=mock_pulp)
            pulp_user = juicer.pulp.User(None)
            # false for the case where user not updated because it didn't exist
            updated = pulp_user.update(login='test-user',
                                       password='sw337',
                                       name='New Name',
                                       environment='re',
                                       roles=['super-users'])
            self.assertFalse(updated)
