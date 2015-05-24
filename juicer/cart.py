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

from pymongo import MongoClient
from pymongo import errors as MongoErrors
import bitmath
import json
import logging
import magic
import os
import os.path
import progressbar
import re
import urllib2

from juicer.common import Constants
from juicer.config import Config
import juicer.pulp


class Cart(object):
    def __init__(self, name, description=None, autoload=False, autosync=False, autosave=False):
        self.output = logging.getLogger('juicer')
        self.name = name
        self.cart_file = os.path.join(Constants.CART_LOCATION, "%s.json" % self.name)
        self.repo_items_hash = {}
        self.remotes_storage = os.path.expanduser(os.path.join(Constants.CART_LOCATION, "%s-remotes" % self.name))
        self.config = Config()

        if autoload:
            self.output.debug("[CART:%s] Auto-loading cart items" % self.name)
            self.load()

        if description is not None:
            for repo_items in description:
                (repo, items) = (repo_items[0], repo_items[1:])
                self.output.debug("Processing %s input items for repo %s"
                                  % (len(items), repo))
                self[repo] = items
            if autosave:
                self.save(remote_save=False)

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
            new_item = CartItem(item)
            cart_items.append(new_item)
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

    def save(self, remote_save=True, warning=False):
        if self.is_empty():
            self.output.error('Cart is empty, not saving anything')
            return None
        self.save_local(warning=warning)
        if remote_save:
            if 'cart_seeds' in self.config.get(self.config.keys()[0]).keys():
                self.save_remote()
            else:
                self.output.warn('No cart_seeds found in config file. Cart not saved on remote.')
        self.output.info("Saved cart '%s'." % self.name)
        return True

    def save_local(self, warning=False):
        json_body = json.dumps(self._cart_dict())
        if warning and os.path.exists(self.cart_file):
            self.output.warn("Cart file '%s' already exists, overwriting with new data." % self.cart_file)
        f = open(self.cart_file, 'w')
        f.write(json_body)
        f.flush()
        f.close()

    def save_remote(self):
        cart_seeds = self.config.get(self.config.keys()[0])['cart_seeds']
        connection_str = 'mongodb://' + cart_seeds
        mongo = MongoClient(connection_str)
        db = mongo.carts
        try:
            db['carts'].save(self._cart_dict())
        except MongoErrors.AutoReconnect:
            self.output.error("failed to save cart %s on remote" % self.name)

    def pull(self):
        cart_seeds = self.config.get(self.config.keys()[0])['cart_seeds']
        connection_str = 'mongodb://' + cart_seeds
        mongo = MongoClient(connection_str)
        db = mongo.carts
        try:
            json_body = json.dumps(db['carts'].find_one({'_id': self.name}))
            if json_body == 'null':
                self.output.error("cart %s does not exist on remote" % self.name)
            else:
                if os.path.exists(self.cart_file):
                    self.output.warn("Cart file '%s' already exists, overwriting with new data." % self.cart_file)
                f = open(self.cart_file, 'w')
                f.write(json_body)
                f.flush()
                f.close()
        except MongoErrors.AutoReconnect:
            self.output.error("failed to find cart %s on remote" % self.name)

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

        # rm in mongo
        if 'cart_seeds' in self.config.get(self.config.keys()[0]).keys():
            cart_seeds = self.config.get(self.config.keys()[0])['cart_seeds']
            connection_str = 'mongodb://' + cart_seeds
            mongo = MongoClient(connection_str)
            db = mongo.carts
            try:
                db['carts'].remove({'_id': self.name})
            except MongoErrors.AutoReconnect:
                self.output.error("failed to save cart %s on remote" % self.name)

    def update(self, description):
        for repo_items in description:
            (repo, items) = (repo_items[0], repo_items[1:])
            if repo not in self.keys():
                self[repo] = items
            else:
                for item in items:
                    self[repo].append(CartItem(item))
        self.save()
        return True

    def upload_items(self, environment, connection, force):
        if not force:
            if not self.verify_remote():
                self.output.warning("Cart differs from remote, use -f to force the push")
                raise SystemError("Cart differs from remote, use -f to force the push")
        pulp_upload = juicer.pulp.Upload(connection)
        for repo, items in self.iterrepos():
            for item in items:
                if not item.synced:
                    item.sync(self.remotes_storage)
                pulp_upload.upload(item.path, repo, item.item_type, environment)
                # Only update path to remote path if the item is an rpm
                if item.item_type == 'rpm':
                    item.path = "https://{0}/pulp/repos/{1}/{2}/{3}".format(connection.host, environment, repo, item.name)
        for repo, items in self.iterrepos():
            pulp_repo = juicer.pulp.Repo(connection)
            pulp_repo.publish(repo, items[0].item_type, environment)
        self.save(warning=False)

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

    def verify_remote(self):
        if 'cart_seeds' in self.config.get(self.config.keys()[0]).keys():
            cart_seeds = self.config.get(self.config.keys()[0])['cart_seeds']
            connection_str = 'mongodb://' + cart_seeds
            mongo = MongoClient(connection_str)
            db = mongo.carts
            try:
                json_body = json.dumps(db['carts'].find_one({'_id': self.name}))
                if json_body == 'null':
                    return True
                else:
                    if json_body == json.dumps(self._cart_dict()):
                        return True
                    else:
                        return False
            except MongoErrors.AutoReconnect:
                self.output.error("failed to find cart %s on remote" % self.name)
                return False


class CartItem(object):
    def __init__(self, source):
        self.output = logging.getLogger('juicer')
        self.name = os.path.basename(source)
        # Source is the original location of this file. That includes
        # both http://.... files and local /home/user/... files.
        self.source = source

        # Assume item is local.
        self.path = os.path.abspath(source)
        self.synced = True

        # If the item is remote, let's change what we know.
        url_regex = re.compile(r'^(http)s?://')
        if url_regex.match(self.source):
            self.path = None
            self.synced = False

        self.item_type = self._set_item_type() if self.path else None

    def _set_item_type(self):
        mime_type = magic.from_file(self.path).lower()
        item_type = None
        if 'rpm' in mime_type.lower():
            item_type = 'rpm'
        elif 'tar' in mime_type.lower():
            item_type = 'docker_image'
        return item_type

    def sync(self, destination):
        dest_file = os.path.join(destination, self.name)

        if not os.path.exists(destination):
            os.mkdir(destination)

        self.path = dest_file
        self.output.debug("Beginning remote->local sync: %s->%s" % (self.source, self.path))

        # An array of widgets to design our progress bar.
        widgets = ['Downloading %s ' % self.name,
                   progressbar.Percentage(), ' ',
                   progressbar.Bar(marker=progressbar.RotatingMarker()), ' ',
                   progressbar.ETA(), ' ',
                   bitmath.integrations.BitmathFileTransferSpeed()]

        u = urllib2.urlopen(self.source)
        f = open(self.path, 'wb')
        meta = u.info()
        item_size = int(meta.getheaders("Content-Length")[0])
        pbar = progressbar.ProgressBar(
            widgets=widgets,
            maxval=item_size).start()
        downloaded = 0
        while True:
            buffer = u.read(Constants.DOWNLOAD_AT_ONCE)
            if not buffer:
                break
            f.write(buffer)
            downloaded += len(buffer)
            if downloaded < pbar.maxval:
                pbar.update(int(downloaded))
        f.close()
        pbar.finish()

        self.modified = True
        self.synced = True
        self.item_type = self._set_item_type()

    def __str__(self):
        return self.path if self.path else self.source
