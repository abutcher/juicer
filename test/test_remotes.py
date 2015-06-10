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

import juicer.remotes

class TestRemotes(TestCase):
    def setUp(self):
        pass

    def test_classify_remotes(self):
        """Can classify remote item types"""
        resource_type = juicer.remotes.classify_resource_type("http://example.com/file.rpm", r'(.+)\.rpm')
        self.assertEqual(resource_type, juicer.remotes.REMOTE_PKG_TYPE)
        resource_type = juicer.remotes.classify_resource_type("http://example.com/stuff/", r'(.+)\.rpm')
        self.assertEqual(resource_type, juicer.remotes.REMOTE_INDEX_TYPE)
        resource_type = juicer.remotes.classify_resource_type("share/juicer/empty-0.1-1.noarch.rpm", r'(.+)\.rpm')
        self.assertEqual(resource_type, juicer.remotes.REMOTE_INPUT_FILE_TYPE)
        resource_type = juicer.remotes.classify_resource_type("potato", r'(.+)\.rpm')
        self.assertEqual(resource_type, None)

    def test_parse_directory_index(self):
        """Can parse a directory index"""
        site_index = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
        <html>
        <head>
        <title>Index of /pulp/repos/re/test</title>
        </head>
        <body>
        <h1>Index of /pulp/repos/re/test</h1>
        <ul><li><a href="/pulp/repos/re/"> Parent Directory</a></li>
        <li><a href="repodata/"> repodata/</a></li>
        <li><a href="versionmerge-1.0.8-1.fc20.noarch.rpm"> versionmerge-1.0.8-1.fc20.noarch.rpm</a></li>
        </ul>
        </body></html>"""
        with mock.patch('urllib2.urlopen') as urlopen:
            urlopen.return_value = site_index
            remote_list = juicer.remotes.parse_directory_index('http://test.com/pulp/repos/re/test', r'(.+)\.rpm')
            self.assertEqual(remote_list, [u'http://test.com/pulp/repos/re/test/versionmerge-1.0.8-1.fc20.noarch.rpm'])

    def test_assemble_remotes(self):
        """Can assemble remotes"""
        site_index = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
        <html>
        <head>
        <title>Index of /pulp/repos/re/test</title>
        </head>
        <body>
        <h1>Index of /pulp/repos/re/test</h1>
        <ul><li><a href="/pulp/repos/re/"> Parent Directory</a></li>
        <li><a href="repodata/"> repodata/</a></li>
        <li><a href="versionmerge-1.0.8-1.fc20.noarch.rpm"> versionmerge-1.0.8-1.fc20.noarch.rpm</a></li>
        </ul>
        </body></html>"""
        with mock.patch('urllib2.urlopen') as urlopen:
            urlopen.return_value = site_index

            # Remote file
            remotes = juicer.remotes.assemble_remotes('http://example.com/file.rpm', r'(.+)\.rpm')
            self.assertEqual(remotes, ['http://example.com/file.rpm'])
            # Remote file index
            remotes = juicer.remotes.assemble_remotes('http://test.com/pulp/repos/re/test', r'(.+)\.rpm')
            self.assertEqual(remotes, [u'http://test.com/pulp/repos/re/test/versionmerge-1.0.8-1.fc20.noarch.rpm'])
            # Local file
            remotes = juicer.remotes.assemble_remotes('share/juicer/empty-0.1-1.noarch.rpm', r'(.+)\.rpm')
            self.assertEqual(remotes, [])

    def test_filter_items(self):
        """Can filter a list of items"""
        site_index = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
        <html>
        <head>
        <title>Index of /pulp/repos/re/test</title>
        </head>
        <body>
        <h1>Index of /pulp/repos/re/test</h1>
        <ul><li><a href="/pulp/repos/re/"> Parent Directory</a></li>
        <li><a href="repodata/"> repodata/</a></li>
        <li><a href="versionmerge-1.0.8-1.fc20.noarch.rpm"> versionmerge-1.0.8-1.fc20.noarch.rpm</a></li>
        </ul>
        </body></html>"""
        with mock.patch('urllib2.urlopen') as urlopen:
            urlopen.return_value = site_index

            # Remote file
            repo_items = [['test-repo', 'http://example.com/file.rpm']]
            filtered_repo_hash = juicer.remotes.filter_items(repo_items, 'rpm')
            self.assertEqual(filtered_repo_hash, {'test-repo': ['http://example.com/file.rpm']})
            # Remote file index
            repo_hash = [['test-repo', 'http://example.com/pulp/repos/re/test']]
            filtered_repo_hash = juicer.remotes.filter_items(repo_hash, 'rpm')
            self.assertEqual(filtered_repo_hash, {'test-repo': ['http://example.com/pulp/repos/re/test/versionmerge-1.0.8-1.fc20.noarch.rpm']})
            # Local file
            repo_items = [['test-repo', 'share/juicer/empty-0.1-1.noarch.rpm']]
            filtered_repo_hash = juicer.remotes.filter_items(repo_items, 'rpm')
            self.assertEqual(filtered_repo_hash, {'test-repo': ['share/juicer/empty-0.1-1.noarch.rpm']})
            # Something that should get removed
            repo_items = [['test-repo', 'potato']]
            filtered_repo_hash = juicer.remotes.filter_items(repo_items, 'rpm')
            self.assertEqual(filtered_repo_hash, {'test-repo': []})
