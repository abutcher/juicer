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

import bitmath
import bitmath.integrations
import json
import logging
import os
import os.path
import progressbar
import pymongo
import pymongo.errors
import re
import shutil
import ssl
import urllib2

import juicer.common
import juicer.plugins
import juicer.pulp
import juicer.remotes
import juicer.types
from juicer.config import Config


class Cart(object):
    def __init__(self, name, description=None, cart_type='rpm', autoload=False, autosync=False, autosave=False, force=False):
        self.output = logging.getLogger('juicer')
        self.name = name
        self.cart_file = os.path.join(juicer.common.Constants.CART_LOCATION,
                                      "{}.json".format(self.name))
        self.repo_items_hash = {}
        self.remotes_storage = os.path.expanduser(os.path.join(juicer.common.Constants.CART_LOCATION,
                                                               "{}-remotes".format(self.name)))
        self.config = Config()

        self.cart_type = cart_type
        if cart_type == 'rpm':
            self.type_object = juicer.types.RPM
        elif cart_type == 'docker':
            self.type_object = juicer.types.Docker
        elif cart_type == 'iso':
            self.type_object = juicer.types.Iso
        else:
            self.type_object = None

        if autoload:
            self.output.debug("[CART:{}] Auto-loading cart items".format(self.name))
            self.load()

        if description is not None:
            for repo, items in description.iteritems():
                self.output.debug("Processing {num} input items for repo {repo}".format(num=len(items), repo=repo))
                self[repo] = items
            if autosave:
                self.save(remote_save=True, force=force)

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
        self.output.debug("[CART:{name}] Adding {count} items to {repo}".format(
            name=self.name,
            count=len(items),
            repo=repo_name))
        cart_items = []
        for item in items:
            self.output.debug("Creating Cart for {}".format(item))
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

    def items(self):
        item_list = []
        for repo, items in self.repo_items_hash.iteritems():
            item_list += items
        return item_list

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

    def save(self, remote_save=True, warning=False, force=False):
        if self.is_empty():
            self.output.error('Cart is empty, not saving anything')
            return False
        self.save_local(warning=warning)
        if remote_save:
            if 'cart_seeds' in self.config.get(self.config.keys()[0]).keys():
                self.save_remote(force=force)
            else:
                self.output.warn('No cart_seeds found in config file. Cart not saved on remote.')
        self.output.info("Saved cart '{cart}'".format(cart=self.name))
        return True

    def save_local(self, warning=False):
        json_body = json.dumps(self._cart_dict())
        if warning and os.path.exists(self.cart_file):  # Sometimes we don't want to show this warning.
            self.output.warn("Cart file '{cart}' already exists, overwriting with new data".format(cart=self.cart_file))
        if not os.path.exists(juicer.common.Constants.CART_LOCATION):
            os.mkdir(juicer.common.Constants.CART_LOCATION)
        f = open(self.cart_file, 'w')
        f.write(json_body)
        f.flush()
        f.close()

    def save_remote(self, force=False):
        if not force:
            if not self.verify_remote():
                raise SystemExit("A remote cart with the same name exists and has different content, use -f to force create.")
        cart_seeds = self.config.get(self.config.keys()[0])['cart_seeds']
        connection_str = 'mongodb://' + cart_seeds
        mongo = pymongo.MongoClient(connection_str)
        db = mongo.carts
        try:
            db['carts'].save(self._cart_dict())
        except pymongo.errors.AutoReconnect:
            self.output.error("Failed to save cart '{cart}' on remote".format(cart=self.name))

    def pull(self):
        cart_seeds = self.config.get(self.config.keys()[0])['cart_seeds']
        connection_str = 'mongodb://' + cart_seeds
        mongo = pymongo.MongoClient(connection_str)
        db = mongo.carts
        try:
            json_body = json.dumps(db['carts'].find_one({'_id': self.name}))
            if json_body == 'null':
                self.output.error("Cart {} does not exist on remote".format(self.name))
            else:
                if os.path.exists(self.cart_file):
                    self.output.warn("Cart file '{}' already exists, overwriting with new data.".format(self.cart_file))
                f = open(self.cart_file, 'w')
                f.write(json_body)
                f.flush()
                f.close()
                self.output.info("Successfully pulled cart '{cart}' from remote".format(cart=self.name))
        except pymongo.errors.AutoReconnect:
            self.output.error("Failed to find cart '{cart}' on remote".format(cart=self.name))

    def load(self):
        """
        Build a cart from a json file
        """
        if not os.path.exists(self.cart_file):
            raise SystemExit("No cart file could be found: {cart_file}".format(cart_file=self.cart_file))

        cart_file = open(self.cart_file)
        cart_body = json.loads(cart_file.read())
        cart_file.close()

        self.cart_type = cart_body['type']

        if self.cart_type == 'rpm':
            self.type_object = juicer.types.RPM
        elif self.cart_type == 'docker':
            self.type_object = juicer.types.Docker
        elif self.cart_type == 'iso':
            self.type_object = juicer.types.Iso
        else:
            self.type_object = None

        for repo, items in cart_body['repos_items'].iteritems():
            self.add_repo(repo, items)

    def delete(self, local=False, remote=False):
        """
        Remove all trace of this cart: delete the file(s) on the local
        filesystem and delete the entry from the database
        """
        self.output.debug("Deleting cart {}".format(self.name))

        if local and not remote:  # User only specified local.
            self.delete_local()
        elif remote and not local:  # User only specified remote
            self.delete_remote()
        else:  # User didn't specify, do both.
            self.delete_local()
            self.delete_remote()

    def delete_local(self):
        # rm -r self.remotes_storage()
        if os.path.exists(self.remotes_storage):
            shutil.rmtree(self.remotes_storage)

        # rm cart_file()
        if os.path.exists(self.cart_file):
            self.output.debug("Removing {cart}'s cart file".format(cart=self.name))
            os.remove(self.cart_file)

        self.output.info("Successfully deleted cart '{cart}' locally".format(cart=self.name))

    def delete_remote(self):
        # rm in mongo
        if 'cart_seeds' in self.config.get(self.config.keys()[0]).keys():
            cart_seeds = self.config.get(self.config.keys()[0])['cart_seeds']
            connection_str = 'mongodb://' + cart_seeds
            mongo = pymongo.MongoClient(connection_str)
            db = mongo.carts
            try:
                db['carts'].remove({'_id': self.name})
                self.output.info("Successfully deleted cart '{cart}' on remote".format(cart=self.name))
            except pymongo.errors.AutoReconnect:
                self.output.error("Failed to delete cart '{cart}' on remote".format(self.name))

    def update(self, description):
        for repo, items in description:
            if repo not in self.keys():
                self[repo] = items
            else:
                for item in items:
                    self[repo].append(CartItem(item))
        self.save(remote_save=True, force=True)
        return True

    def upload_items(self, environment, connection, force):
        if not force:
            if not self.verify_remote():
                raise SystemExit("Local cart differs from remote, use -f to force upload")

        ######################################################################
        # Ensure repositories exist before we do any work
        ######################################################################
        pulp_repo = juicer.pulp.Repo(connection)
        for repo, items in self.iterrepos():
            # Make sure the repo exists before we upload items
            exists = pulp_repo.exists(repo, environment)
            if not exists:
                raise SystemExit("Repo '{repo}' does not exist in '{environment}'".format(
                    repo=repo, environment=environment))

        pulp_upload = juicer.pulp.Upload(connection)

        ######################################################################
        # Sync remote items before we do anything else
        ######################################################################
        for repo, items in self.iterrepos():
            for item in items:
                if not item.synced:
                    item.sync(self.remotes_storage)

        ######################################################################
        # Execute pre plugins
        ######################################################################
        plugins = juicer.plugins.Plugins()
        plugins.execute_pre_plugins(self.cart_type, environment, self.items())

        ######################################################################
        # Generate upload requests
        ######################################################################
        widgets = ['Initializing ',
                   progressbar.Percentage(), ' ',
                   progressbar.Bar(marker=progressbar.RotatingMarker()), ' ',
                   progressbar.ETA()]
        initialize_pbar = progressbar.ProgressBar(
            widgets=widgets,
            maxval=len(self.items())).start()
        item_count = 0
        for repo, items in self.iterrepos():
            for item in items:
                item.upload_id = pulp_upload.initialize_upload()
                item_count += 1
                initialize_pbar.update(item_count)
        initialize_pbar.finish()

        ######################################################################
        # Upload items
        ######################################################################
        total_size = 0
        for repo, items in self.iterrepos():
            for item in items:
                total_size += os.path.getsize(item.path)
        widgets = ['Uploading ',
                   progressbar.Percentage(), ' ',
                   progressbar.Bar(marker=progressbar.RotatingMarker()), ' ',
                   progressbar.ETA(), ' ',
                   bitmath.integrations.BitmathFileTransferSpeed()]
        upload_pbar = progressbar.ProgressBar(
            widgets=widgets,
            maxval=int(total_size)).start()
        for repo, items in self.iterrepos():
            for item in items:
                pulp_upload.upload(item.upload_id, item.path, repo, upload_pbar)
        upload_pbar.finish()

        ######################################################################
        # Import uploads
        ######################################################################
        widgets = ['Importing ',
                   progressbar.Percentage(), ' ',
                   progressbar.Bar(marker=progressbar.RotatingMarker()), ' ',
                   progressbar.ETA()]
        import_pbar = progressbar.ProgressBar(
            widgets=widgets,
            maxval=len(self.items())).start()
        item_count = 0
        tasks = []
        for repo, items in self.iterrepos():
            repo_id = "{0}-{1}".format(repo, environment)
            for item in items:
                if self.cart_type == 'docker':
                    unit_type = 'docker_image'
                else:
                    unit_type = self.cart_type
                unit_key, unit_metadata = self.type_object(item.path).generate_upload_data()
                # Keep tasks returned from import upload so we can make sure they've finished
                tasks.append(pulp_upload.import_upload(upload_id=item.upload_id,
                                                       repo_id=repo_id,
                                                       unit_type=unit_type,
                                                       unit_key=unit_key,
                                                       unit_metadata=unit_metadata))
                item_count += 1
                import_pbar.update(item_count)
                # Only update path to remote path if the item is iso or rpm
                if self.cart_type in ['rpm', 'iso']:
                    item.path = "https://{host}/pulp/repos/{environment}/{repo}/{name}".format(
                        host=connection.host,
                        environment=environment,
                        repo=repo,
                        name=item.name)
        import_pbar.finish()

        ######################################################################
        # Wait for the imports to finish before we delete remote upload
        ######################################################################
        pulp_task = juicer.pulp.Task(connection)
        waiting_pbar = progressbar.ProgressBar(widgets=['Waiting for imports to finish ', progressbar.AnimatedMarker()])
        for task in waiting_pbar(tasks):
            pulp_task.wait_for(task.spawned_tasks[0].task_id)

        ######################################################################
        # Clean up upload requests
        ######################################################################
        widgets = ['Cleaning ',
                   progressbar.Percentage(), ' ',
                   progressbar.Bar(marker=progressbar.RotatingMarker()), ' ',
                   progressbar.ETA()]
        cleanup_pbar = progressbar.ProgressBar(
            widgets=widgets,
            maxval=len(self.items())).start()
        item_count = 0
        for repo, items in self.iterrepos():
            for item in items:
                pulp_upload.delete_upload(item.upload_id)
                item_count += 1
                cleanup_pbar.update(item_count)
        cleanup_pbar.finish()

        ######################################################################
        # Publish repositories
        ######################################################################
        widgets = ['Publishing ',
                   progressbar.Percentage(), ' ',
                   progressbar.Bar(marker=progressbar.RotatingMarker()), ' ',
                   progressbar.ETA()]
        publish_pbar = progressbar.ProgressBar(
            widgets=widgets,
            maxval=len(self.repos())).start()
        repo_count = 0
        for repo, items in self.iterrepos():
            pulp_repo.publish(repo, environment)
            repo_count += 1
            publish_pbar.update(repo_count)
        publish_pbar.finish()

        ######################################################################
        # Save the cart
        ######################################################################
        self.save(warning=False)

        ######################################################################
        # Execute post plugins
        ######################################################################
        plugins = juicer.plugins.Plugins()
        plugins.execute_post_plugins(self.cart_type, environment, self.items())

    def __str__(self):
        return json.dumps(self._cart_dict(), indent=4)

    def _cart_dict(self):
        output = {'_id': self.name,
                  'type': self.cart_type,
                  'repos_items': []}

        repos_items = {}
        for repo in self.repos():
            repos_items[repo] = [str(i) for i in self[repo]]

        output['repos_items'] = repos_items
        return output

    def verify_remote(self):
        """
        Checks if the remote cart exists.
        Checks if remote cart is different that the local cart.
        """
        if 'cart_seeds' in self.config.get(self.config.keys()[0]).keys():
            cart_seeds = self.config.get(self.config.keys()[0])['cart_seeds']
            connection_str = 'mongodb://' + cart_seeds
            mongo = pymongo.MongoClient(connection_str)
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
            except pymongo.errors.AutoReconnect:
                self.output.error("Failed to find cart '{cart}' on remote".format(cart=self.name))
                return False


class CartItem(object):
    def __init__(self, source):
        self.output = logging.getLogger('juicer')
        self.name = os.path.basename(source)

        self.upload_id = None

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

    def sync(self, destination):
        dest_file = os.path.join(destination, self.name)

        if not os.path.exists(destination):
            os.mkdir(destination)

        self.path = dest_file

        self.output.debug("Beginning remote->local sync: {source}->{path}".format(
            source=self.source,
            path=self.path))

        # An array of widgets to design our progress bar.
        widgets = ['Downloading {} '.format(self.name),
                   progressbar.Percentage(), ' ',
                   progressbar.Bar(marker=progressbar.RotatingMarker()), ' ',
                   progressbar.ETA(), ' ',
                   bitmath.integrations.BitmathFileTransferSpeed()]

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        u = urllib2.urlopen(self.source, context=ctx)
        f = open(self.path, 'wb')
        meta = u.info()
        item_size = int(meta.getheaders("Content-Length")[0])
        pbar = progressbar.ProgressBar(
            widgets=widgets,
            maxval=item_size).start()
        downloaded = 0
        while True:
            buffer = u.read(juicer.common.Constants.DOWNLOAD_AT_ONCE)
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

    def __str__(self):
        return self.path if self.path else self.source
