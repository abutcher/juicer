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


class TestPulpRepo(TestCase):
    def setUp(self):
        pass

    def test_pulp_repo_create(self):
        """Verify pulp repo create"""
        with mock.patch('pulp.bindings.repository') as repository:
            # Return value for the create_and_configure() method call (RepositoryAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 201
            mock_pulp = mock.Mock(create_and_configure=mock.MagicMock(return_value=mock_response))
            
            # (pulp.bindings).repository.RepositoryAPI
            repository.RepositoryAPI = mock.Mock(return_value=mock_pulp)

            pulp_repo = juicer.pulp.PulpRepo.PulpRepo(None)
            created = pulp_repo.create(name='test-repo',
                                       environment='re')
            self.assertTrue(created)

            mock_response.response_code = 400
            created = pulp_repo.create(name='test-repo',
                                       environment='re')
            self.assertFalse(created)

    def test_pulp_repo_delete(self):
        """Verify pulp repo delete"""
        with mock.patch('pulp.bindings.repository') as repository:
            # Return value for the delete() method call (RepositoryAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 202
            mock_pulp = mock.Mock(delete=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).repository.RepositoryAPI
            repository.RepositoryAPI = mock.Mock(return_value=mock_pulp)
            pulp_repo = juicer.pulp.PulpRepo.PulpRepo(None)
            deleted = pulp_repo.delete(name='test-repo',
                                   environment='re')
            # true for the case where repo deleted
            self.assertTrue(deleted)

            mock_response.response_code = 400
            deleted = pulp_repo.delete(name='test-repo',
                                   environment='re')
            # false for the case where repo not deleted
            self.assertFalse(deleted)

    def test_pulp_repo_list(self):
        """Verify pulp repo list"""
        with mock.patch('pulp.bindings.repository') as repository:
            # Return value for the list() method call (RepositoryAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 200
            mock_response.response_body = [{'id': 'test-repo-re', 'display_name': 'test-repo'}]
            mock_pulp = mock.Mock(repositories=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).repository.RepositoryAPI
            repository.RepositoryAPI = mock.Mock(return_value=mock_pulp)
            pulp_repo = juicer.pulp.PulpRepo.PulpRepo(None)
            listed = pulp_repo.list(environment='re')
            # true for the case where repo listed
            self.assertTrue(listed)

            mock_response.response_code = 400
            listed = pulp_repo.list(environment='re')
            # false for the case where repo not listed
            self.assertFalse(listed)

    def test_pulp_repo_publish(self):
        """Verify pulp repo publish"""
        with mock.patch('pulp.bindings.repository') as repository:
            # Return value for the publish() method call (RepositoryActionsAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 202
            mock_pulp = mock.Mock(publish=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).repository.RepositoryActionsAPI
            repository.RepositoryActionsAPI = mock.Mock(return_value=mock_pulp)
            pulp_repo = juicer.pulp.PulpRepo.PulpRepo(None)
            published = pulp_repo.publish(name='test-repo',
                                          environment='re')
            # true for the case where repo published
            self.assertTrue(published)

            mock_response.response_code = 400
            published = pulp_repo.publish(name='test-repo',
                                          environment='re')
            # false for the case where repo not published
            self.assertFalse(published)

    def test_pulp_repo_show(self):
        """Verify pulp repo show"""
        with mock.patch('pulp.bindings.repository') as repository:
            # Return value for the repository() method call (RepositoryAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 200
            mock_response.response_body = {'display_name':'test-repo',
                                           'content_unit_counts':{'rpm': 0}}
            mock_pulp = mock.Mock(repository=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).repository.RepositoryActionsAPI
            repository.RepositoryAPI = mock.Mock(return_value=mock_pulp)
            pulp_repo = juicer.pulp.PulpRepo.PulpRepo(None)
            shown = pulp_repo.show(name='test-repo',
                                   environment='re')
            # true for the case where repo shown
            self.assertTrue(shown)

            shown = pulp_repo.show(name='test-repo',
                                   environment='re',
                                   json=True)
            # true for the case where repo shown
            self.assertTrue(shown)

            mock_response.response_code = 400
            shown = pulp_repo.show(name='test-repo',
                                   environment='re')
            # false for the case where repo not shown
            self.assertFalse(shown)
