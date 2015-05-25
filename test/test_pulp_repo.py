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


class TestRepo(TestCase):
    def setUp(self):
        pass

    def test_pulp_repo_exists(self):
        """Verify pulp repo ensure exists"""
        with mock.patch('pulp.bindings.repository') as repository:
            # Return value for the repository() method call (RepositoryAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 200
            mock_response.response_body = {'display_name':'test-repo',
                                           'content_unit_counts':{'rpm': 0}}
            mock_pulp = mock.Mock(repository=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).repository.RepositoryActionsAPI
            repository.RepositoryAPI = mock.Mock(return_value=mock_pulp)
            pulp_repo = juicer.pulp.Repo(None)
            exists = pulp_repo.exists(name='test-repo',
                                      environment='re')
            # true for the case where repo exists
            self.assertTrue(exists)

            mock_pulp = mock.Mock(repository=mock.MagicMock(side_effect=pulp.bindings.exceptions.NotFoundException({'_href': 'oh no'})))
            repository.RepositoryAPI = mock.Mock(return_value=mock_pulp)
            pulp_repo = juicer.pulp.Repo(None)
            # false for the case where repo doesn't exist
            exists = pulp_repo.exists(name='test-repo',
                                      environment='re')
            self.assertFalse(exists)

    def test_pulp_repo_create(self):
        """Verify pulp repo create"""
        with mock.patch('pulp.bindings.repository') as repository:
            # Return value for the create_and_configure() method call (RepositoryAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 201
            mock_pulp = mock.Mock(create_and_configure=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).repository.RepositoryAPI
            repository.RepositoryAPI = mock.Mock(return_value=mock_pulp)

            pulp_repo = juicer.pulp.Repo(None)
            created = pulp_repo.create(name='test-repo',
                                       repotype='rpm',
                                       environment='re')
            # true for the case where repo created
            self.assertTrue(created)

            pulp_repo = juicer.pulp.Repo(None)
            created = pulp_repo.create(name='test-repo',
                                       repotype='docker',
                                       environment='re')
            # true for the case where repo created
            self.assertTrue(created)

            pulp_repo = juicer.pulp.Repo(None)
            created = pulp_repo.create(name='test-repo',
                                       repotype='iso',
                                       environment='re')
            # true for the case where repo created
            self.assertTrue(created)

            mock_response.response_code = 400
            created = pulp_repo.create(name='test-repo',
                                       repotype='rpm',
                                       environment='re')
            # true for the case where repo not created
            self.assertFalse(created)

            mock_pulp = mock.Mock(create_and_configure=mock.MagicMock(side_effect=pulp.bindings.exceptions.ConflictException({'_href': 'oh no'})))
            repository.RepositoryAPI = mock.Mock(return_value=mock_pulp)
            pulp_repo = juicer.pulp.Repo(None)
            # false for the case where repo not created due to a conflict
            created = pulp_repo.create(name='test-repo',
                                       repotype='rpm',
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
            pulp_repo = juicer.pulp.Repo(None)
            deleted = pulp_repo.delete(name='test-repo',
                                   environment='re')
            # true for the case where repo deleted
            self.assertTrue(deleted)

            mock_response.response_code = 400
            deleted = pulp_repo.delete(name='test-repo',
                                   environment='re')
            # false for the case where repo not deleted
            self.assertFalse(deleted)

            mock_pulp = mock.Mock(delete=mock.MagicMock(side_effect=pulp.bindings.exceptions.NotFoundException({'_href': 'oh no'})))
            repository.RepositoryAPI = mock.Mock(return_value=mock_pulp)
            pulp_repo = juicer.pulp.Repo(None)
            # false for the case where repo not deleted because it didn't exist
            deleted = pulp_repo.delete(name='test-repo',
                                       environment='re')
            self.assertFalse(deleted)

    def test_pulp_repo_list(self):
        """Verify pulp repo list"""
        with mock.patch('pulp.bindings.repository') as repository:
            # Return value for the repositories() method call (RepositoryAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 200
            mock_response.response_body = [{'id': 'test-repo-re', 'display_name': 'test-repo'}]
            mock_pulp = mock.Mock(repositories=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).repository.RepositoryAPI
            repository.RepositoryAPI = mock.Mock(return_value=mock_pulp)
            pulp_repo = juicer.pulp.Repo(None)
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
            mock_publish_response = mock.MagicMock()
            mock_publish_response.response_code = 202
            mock_publish = mock.Mock(publish=mock.MagicMock(return_value=mock_publish_response))

            mock_distributor_response = mock.MagicMock()
            mock_distributor_response.response_code = 200
            mock_distributor_response.response_body = [{'id': 'test_distributor'}]
            mock_distributor = mock.Mock(distributors=mock.MagicMock(return_value=mock_distributor_response))

            # (pulp.bindings).repository.RepositoryActionsAPI
            repository.RepositoryActionsAPI = mock.Mock(return_value=mock_publish)
            # (pulp.bindings).repository.RepositoryActionsAPI
            repository.RepositoryDistributorAPI = mock.Mock(return_value=mock_distributor)

            pulp_repo = juicer.pulp.Repo(None)
            published = pulp_repo.publish(name='test-repo',
                                          environment='re')
            # true for the case where repo published
            self.assertTrue(published)

            mock_publish_response.response_code = 400
            published = pulp_repo.publish(name='test-repo',
                                          environment='re')
            # false for the case where repo not published
            self.assertFalse(published)

            mock_publish = mock.Mock(publish=mock.MagicMock(side_effect=pulp.bindings.exceptions.NotFoundException({'_href': 'oh no'})))
            repository.RepositoryActionsAPI = mock.Mock(return_value=mock_publish)
            pulp_repo = juicer.pulp.Repo(None)
            # false for the case where repo not published because it didn't exist
            published = pulp_repo.publish(name='test-repo',
                                          environment='re')
            self.assertFalse(published)

    def test_pulp_repo_remove(self):
        """Verify pulp repo remove"""
        with mock.patch('pulp.bindings.repository') as repository:
            # Return value for the remove() method call (RepositoryUnitAPI Class method)
            mock_response = mock.MagicMock()
            mock_response.response_code = 202
            mock_pulp = mock.Mock(remove=mock.MagicMock(return_value=mock_response))

            # (pulp.bindings).repository.RepositoryUnitAPI
            repository.RepositoryUnitAPI = mock.Mock(return_value=mock_pulp)
            pulp_repo = juicer.pulp.Repo(None)
            removed = pulp_repo.remove(name='test-repo',
                                       environment='re',
                                       item_type='rpm',
                                       glob="empty")
            # true for the case where units removed
            self.assertTrue(removed)

            mock_response.response_code = 400
            removed = pulp_repo.remove(name='test-repo',
                                       environment='re',
                                       item_type='rpm',
                                       glob="empty")
            # false for the case where units not removed
            self.assertFalse(removed)

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
            pulp_repo = juicer.pulp.Repo(None)
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

            mock_pulp = mock.Mock(repository=mock.MagicMock(side_effect=pulp.bindings.exceptions.NotFoundException({'_href': 'oh no'})))
            repository.RepositoryAPI = mock.Mock(return_value=mock_pulp)
            pulp_repo = juicer.pulp.Repo(None)
            # false for the case where repo not shown because it didn't exist
            shown = pulp_repo.show(name='test-repo',
                                   environment='re')
            self.assertFalse(shown)
