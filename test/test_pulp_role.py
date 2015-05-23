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

class TestRole(TestCase):
    def setUp(self):
        pass

    def test_pulp_role_add_user(self):
        """Verify pulp role add user"""
        with mock.patch('pulp.bindings.auth') as auth:
            # Return value for the add_user() method call (RoleAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 200
            mock_pulp = mock.Mock(add_user=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).auth.RoleAPI
            auth.RoleAPI = mock.Mock(return_value=mock_pulp)

            pulp_role = juicer.pulp.Role(None)
            added = pulp_role.add_user(name='role-name',
                                       environment='re',
                                       login='user-login')
            # true for the case where role added
            self.assertTrue(added)

            mock_response.response_code = 400
            added = pulp_role.add_user(name='role-name',
                                       environment='re',
                                       login='user-login')
            # true for the case where role not created
            self.assertFalse(added)

            mock_pulp = mock.Mock(add_user=mock.MagicMock(side_effect=pulp.bindings.exceptions.NotFoundException({'_href': 'oh no'})))
            auth.RoleAPI = mock.Mock(return_value=mock_pulp)
            pulp_role = juicer.pulp.Role(None)
            # false for the case where role not created due to a conflict
            added = pulp_role.add_user(name='role-name',
                                       environment='re',
                                       login='user-login')
            self.assertFalse(added)

    def test_pulp_role_create(self):
        """Verify pulp role create"""
        with mock.patch('pulp.bindings.auth') as auth:
            # Return value for the create() method call (RoleAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 201
            mock_pulp = mock.Mock(create=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).auth.RoleAPI
            auth.RoleAPI = mock.Mock(return_value=mock_pulp)

            pulp_role = juicer.pulp.Role(None)
            created = pulp_role.create(name='test-role',
                                       environment='re',
                                       description=None)
            # true for the case where role created
            self.assertTrue(created)

            mock_response.response_code = 400
            created = pulp_role.create(name='test-role',
                                       environment='re',
                                       description=None)
            # true for the case where role not created
            self.assertFalse(created)

            mock_pulp = mock.Mock(create=mock.MagicMock(side_effect=pulp.bindings.exceptions.ConflictException({'_href': 'oh no'})))
            auth.RoleAPI = mock.Mock(return_value=mock_pulp)
            pulp_role = juicer.pulp.Role(None)
            # false for the case where role not created due to a conflict
            created = pulp_role.create(name='test-role',
                                       environment='re',
                                       description=None)
            self.assertFalse(created)

    def test_pulp_role_delete(self):
        """Verify pulp role delete"""
        with mock.patch('pulp.bindings.auth') as auth:
            # Return value for the delete() method call (RoleAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 200
            mock_pulp = mock.Mock(delete=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).auth.RoleAPI
            auth.RoleAPI = mock.Mock(return_value=mock_pulp)
            pulp_role = juicer.pulp.Role(None)
            deleted = pulp_role.delete(name='test-role',
                                       environment='re')
            # true for the case where role deleted
            self.assertTrue(deleted)

            mock_response.response_code = 400
            deleted = pulp_role.delete(name='test-role',
                                       environment='re')
            # false for the case where role not deleted
            self.assertFalse(deleted)

            mock_pulp = mock.Mock(delete=mock.MagicMock(side_effect=pulp.bindings.exceptions.NotFoundException({'_href': 'oh no'})))
            auth.RoleAPI = mock.Mock(return_value=mock_pulp)
            pulp_role = juicer.pulp.Role(None)
            # false for the case where role not deleted because it didn't exist
            deleted = pulp_role.delete(name='test-role',
                                       environment='re')
            self.assertFalse(deleted)

    def test_pulp_role_list(self):
        """Verify pulp role list"""
        with mock.patch('pulp.bindings.auth') as auth:
            # Return value for the roles() method call (RoleAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 200
            mock_response.response_body = [{'id': 'test-role', 'display_name': 'test-role'}]
            mock_pulp = mock.Mock(roles=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).auth.RoleAPI
            auth.RoleAPI = mock.Mock(return_value=mock_pulp)
            pulp_role = juicer.pulp.Role(None)
            listed = pulp_role.list(environment='re')
            # true for the case where roles listed
            self.assertTrue(listed)

            mock_response.response_code = 400
            listed = pulp_role.list(environment='re')
            # false for the case where roles not listed
            self.assertFalse(listed)

    def test_pulp_role_remove_user(self):
        """Verify pulp role remove_user"""
        with mock.patch('pulp.bindings.auth') as auth:
            # Return value for the remove_user() method call (RoleAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 200
            mock_pulp = mock.Mock(remove_user=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).auth.RoleAPI
            auth.RoleAPI = mock.Mock(return_value=mock_pulp)
            pulp_role = juicer.pulp.Role(None)
            removed = pulp_role.remove_user(name='test-role',
                                            environment='re',
                                            login='test-user')
            # true for the case where user removed
            self.assertTrue(removed)

            mock_response.response_code = 400
            removed = pulp_role.remove_user(name='test-role',
                                            environment='re',
                                            login='test-user')
            # false for the case where user not removed
            self.assertFalse(removed)

            mock_pulp = mock.Mock(remove_user=mock.MagicMock(side_effect=pulp.bindings.exceptions.NotFoundException({'_href': 'oh no'})))
            auth.RoleAPI = mock.Mock(return_value=mock_pulp)
            pulp_role = juicer.pulp.Role(None)
            # false for the case where user not removed because it didn't exist
            removed = pulp_role.remove_user(name='test-role',
                                            environment='re',
                                            login='test-user')
            self.assertFalse(removed)

    def test_pulp_role_show(self):
        """Verify pulp role show"""
        with mock.patch('pulp.bindings.auth') as auth:
            # Return value for the role() method call (RoleAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 200
            mock_response.response_body = {'display_name':'test-role'}
            mock_pulp = mock.Mock(role=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).auth.RoleAPI
            auth.RoleAPI = mock.Mock(return_value=mock_pulp)
            pulp_role = juicer.pulp.Role(None)
            shown = pulp_role.show(name='test-role',
                                   environment='re')
            # true for the case where role shown
            self.assertTrue(shown)

            # shown = pulp_role.show(name='test-role',
            #                        environment='re',
            #                        json=True)
            # # true for the case where role shown
            # self.assertTrue(shown)

            mock_response.response_code = 400
            shown = pulp_role.show(name='test-role',
                                   environment='re')
            # false for the case where role not shown
            self.assertFalse(shown)

            mock_pulp = mock.Mock(role=mock.MagicMock(side_effect=pulp.bindings.exceptions.NotFoundException({'_href': 'oh no'})))
            auth.RoleAPI = mock.Mock(return_value=mock_pulp)
            pulp_role = juicer.pulp.Role(None)
            # false for the case where role not shown because it didn't exist
            shown = pulp_role.show(name='test-role',
                                   environment='re')
            self.assertFalse(shown)
