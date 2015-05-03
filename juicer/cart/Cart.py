# -*- coding: utf-8 -*-
# Juicer - Administer Pulp and Release Carts
# Copyright © 2015, Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from juicer.common import Constants
from juicer.pulp.Upload import Upload
from juicer.rpm.RPM import RPM
import json
import logging
import os


class Cart(object):
    def __init__(self, name, description=None, autoload=False, autosync=False, autosave=False):
        self.output = logging.getLogger('juicer')
        self.name = name
        self.cart_file = os.path.join(Constants.CART_LOCATION, "%s.json" % self.name)
        self.repo_items_hash = {}
        self.remotes_storage = os.path.expanduser(os.path.join(Constants.CART_LOCATION, "%s-remotes" % self.name))

        if autoload:
            self.output.notice("[CART:%s] Auto-loading cart items" % self.name)
            self.load()

        if description is not None:
            for repo_items in description:
                (repo, items) = (repo_items[0], repo_items[1:])
                self.output.debug("Processing %s input items for repo %s"
                                  % (len(items), repo))
                self[repo] = items
            if autosave:
                self.save()

    def __getitem__(self, repo):
        """ Return the items in the given repo """
        if repo in self.repo_items_hash:
            return self.repo_items_hash[repo]
        else:
            # TODO: Should this raise?
            return None

    def __setitem__(self, repo, items):
        """
        Just provides a shorthand way to call add_repo:

        cart_object['repo'] = items
        """
        self.add_repo(repo, items)

    def add_repo(self, repo_name, items):
        """
        Build up repos

        `name` - Name of this repo.
        `items` - List of paths to rpm.
        """
        self.output.debug("[CART:%s] Adding %s items to repo '%s'" %
                          (self.name, len(items), repo_name))
        # Is some sort of validation required here?
        cart_items = []
        for item in items:
            self.output.debug("Creating CartObject for %s" % item)
            rpm = RPM(item)
            cart_items.append(rpm)
        self.repo_items_hash[repo_name] = cart_items

    def keys(self):
        """
        Get repo keys.
        """
        return self.repo_items_hash.keys()

    def repos(self):
        """
        Return all list of the repos it cart will upload items into.
        """
        return self.repo_items_hash.keys()

    def iterrepos(self):
        """
        A generator function that yields a (repo, [items]) tuple for
        each non-empty repo.
        """
        for repo, items in self.repo_items_hash.iteritems():
            if items:
                yield (repo, items)

    def is_empty(self):
        """
        return True if the cart has no items, False otherwise
        """
        for repo, items in self.iterrepos():
            if items:
                return False
        return True

    def save(self):
        if self.is_empty():
            self.output.error('Cart is empty, not saving anything')
            return None

        json_body = json.dumps(self._cart_dict())
        if os.path.exists(self.cart_file):
            self.output.warn("Cart file '%s' already exists, overwriting with new data." % self.cart_file)
        f = open(self.cart_file, 'w')
        f.write(json_body)
        f.flush()
        f.close()
        self.output.info("Saved cart '%s'." % self.name)

    def load(self):
        """
        Build a cart from a json file
        """
        if not os.path.exists(self.cart_file):
            raise SystemError("No cart file found %s" % self.cart_file)

        cart_file = open(self.cart_file)
        cart_body = json.loads(cart_file.read())
        cart_file.close()

        for repo, items in cart_body['repos_items'].iteritems():
            self.add_repo(repo, items)

    def delete(self):
        """
        Remove all trace of this cart: delete the file(s) on the local
        filesystem and delete the entry from the database
        """
        self.output.debug("Deleting cart %s" % self.name)

        # rm -r self.remotes_storage()
        if os.path.exists(self.remotes_storage):
            for item in os.listdir(self.remotes_storage):
                ipath = os.path.expanduser(self.remotes_storage + '/' + item)
                if os.path.exists(ipath):
                    self.output.debug("removing %s" % ipath)
                    os.remove(ipath)
                self.output.debug("removing %s's remote item storage dir" % self.name)
                os.rmdir(self.remotes_storage)

        # rm cart_file()
        if os.path.exists(self.cart_file):
            self.output.debug("removing %s's cart file" % self.name)
            os.remove(self.cart_file)

    def upload_items(self, environment, connection):
        pulp_upload = Upload(connection)
        for repo, items in self.iterrepos():
            for item in items:
                if not item.synced:
                    item.sync()
                pulp_upload.upload(item.path, repo, environment)

    def __str__(self):
        return json.dumps(self._cart_dict(), indent=4)

    def _cart_dict(self):
        output = {'_id': self.name,
                  'repos_items': []}

        repos_items = {}
        for repo in self.repos():
            repos_items[repo] = [str(i) for i in self[repo]]

        output['repos_items'] = repos_items
        return output
