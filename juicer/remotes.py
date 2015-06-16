# -*- coding: utf-8 -*-
# Copyright © 2008-2011, Red Hat, Inc.
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# This file is taken from the Nushus project <http://fedorahosted.org/nushus/>
"""
Functions for handling remote package resources
"""
import fnmatch
import os.path
import BeautifulSoup
import logging
import re
import urllib2

import juicer.types

REMOTE_PKG_TYPE = 1
REMOTE_INDEX_TYPE = 2
REMOTE_INPUT_FILE_TYPE = 3

output = logging.getLogger('juicer')


def filter_items(repo_items, item_type):
    """
    Filter a list of items into locals and remotes.
    """

    if item_type == 'rpm':
        pattern = juicer.types.RPM(None).pattern
    elif item_type == 'docker':
        pattern = juicer.types.Docker(None).pattern
    elif item_type == 'iso':
        pattern = juicer.types.Iso(None).pattern
    else:
        pattern = juicer.types.RPM(None).pattern

    repo_hash = {}
    for ri in repo_items:
        (repo, items) = (ri[0], ri[1:])

        remote_items = []
        possible_remotes = filter(lambda i: not os.path.exists(i), items)

        output.debug("Considering {number} possible remotes".format(number=len(possible_remotes)))

        for item in possible_remotes:
            remote_items.extend(assemble_remotes(item, pattern))
            output.debug("Remote packages: {remote_items}".format(remote_items=str(remote_items)))

        local_items = filter(os.path.exists, items)
        # Store absolute path for local items
        local_items = map(os.path.abspath, local_items)

        filtered_items = list(set(remote_items + local_items))
        repo_hash[repo] = filtered_items
    return repo_hash


def assemble_remotes(resource, pattern):
    """
    Using the specified input resource, assemble a list of resource URLS.

    This function will, when given a remote package url, directory
    index, or a combination of the two in a local input file, do all
    the work required to turn that input into a list of only remote
    package URLs.

    """
    resource_type = classify_resource_type(resource, pattern)

    if resource_type is None:
        return []
    elif resource_type == REMOTE_PKG_TYPE:
        return [resource]
    elif resource_type == REMOTE_INDEX_TYPE:
        return parse_directory_index(resource, pattern)
    elif resource_type == REMOTE_INPUT_FILE_TYPE:
        # Later on this could examine the excluded data for directory
        # indexes and iterate over those too.
        remote_packages, excluded_data = parse_input_file(resource, pattern)
        return remote_packages


def classify_resource_type(resource, pattern):
    """Determine if the specified resource is remote or local.

    We can handle three remote resource types from the command line,
    remote files, directory indexes, and input files. They're
    classified by matching the following patterns:

    - Remote files appear as http[s]://anything/anything.anything
    - Directory indexes appear as http[s]://anything.anything/anything
    - Input files don't match above, exist() on local filesystem

    """
    if is_directory_index(resource):
        return REMOTE_INDEX_TYPE
    elif is_remote_package(resource, pattern):
        return REMOTE_PKG_TYPE
    elif os.path.exists(os.path.expanduser(resource)):
        return REMOTE_INPUT_FILE_TYPE
    else:
        return None


def is_remote_package(resource, pattern):
    """
    Classify the input resource as a remote resource.
    """
    remote_regexp = re.compile(r"^https?://(.+)\/{pattern}$".format(pattern=pattern), re.I)
    result = remote_regexp.match(resource)

    if result is not None:
        return True
    else:
        return False


def is_directory_index(resource):
    """
    Classify the input resource as a directory index or not.
    """
    if re.compile(r"^https?://(.+)/$", re.I).match(resource):
        return True

    if re.compile(r"^https?://(.+)$", re.I).match(resource):
        if re.compile(r"^[^\[\]\*\?\!]+$", re.I).match(resource):
            if re.compile(r"(.+)[.](.+)").match(os.path.basename(resource)):
                return False
            else:
                return True
        else:
            return True
    else:
        return False


def parse_input_file(resource, pattern):
    """
    Parse input file into remote packages and excluded data.

    In addition to garbage, excluded data includes directory indexes
    for the time being. This will be revisited after basic
    functionality has been fully implemented.
    """
    input_resource = open(resource, 'r').read()
    remotes_list = [url for url in input_resource.split()]
    remote_packages = [pkg for pkg in remotes_list if is_remote_package(pkg, pattern) is True]
    excluded_data = [datum for datum in remotes_list if datum not in remote_packages]
    http_indexes = [index for index in excluded_data if is_directory_index(index)]
    remotes_from_indexes = reduce(lambda x, y: x + parse_directory_index(y, pattern), http_indexes, [])

    return (remote_packages + remotes_from_indexes, excluded_data)


def parse_directory_index(directory_index, pattern):
    """
    Retrieve a directory index and make a list of the resources listed.
    """

    # Use the tail of the remote path to determine what we're dealing with.
    head, tail = os.path.split(directory_index)

    # Is this an fnmatch or a directory without a trailing slash?
    if re.compile(r"^[^\[\]\*\?\!\.]+$", re.I).match(tail):
        if not directory_index.endswith('/'):
            directory_index = directory_index + '/'
        site_index = urllib2.urlopen(directory_index)
    else:
        pattern = fnmatch.translate(tail)
        directory_index = head + '/'
        site_index = urllib2.urlopen(directory_index)

    parsed_site_index = BeautifulSoup.BeautifulSoup(site_index)
    link_tags = parsed_site_index.findAll('a', href=re.compile(pattern))
    # Only save the HREF attribute values from the links found
    names = [str(link['href']) for link in link_tags]

    # Remove items ending in /
    names[:] = [name for name in names if not name.endswith('/')]

    # Join the index path with the discovered names so we only return complete paths
    remote_list = map(lambda end: "".join([directory_index, end]), names)

    return remote_list
