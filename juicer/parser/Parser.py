# -*- coding: utf-8 -*-
# Juicer - Administer Pulp and Release Carts
# Copyright © 2012,2013, Red Hat, Inc.
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

import argparse
import juicer.parser
from juicer.command.CartCreateCommand import CartCreateCommand
from juicer.command.CartDeleteCommand import CartDeleteCommand
from juicer.command.CartShowCommand import CartShowCommand
from juicer.command.HelloCommand import HelloCommand
from juicer.command.RepoCreateCommand import RepoCreateCommand
from juicer.command.RepoDeleteCommand import RepoDeleteCommand
from juicer.command.RepoPublishCommand import RepoPublishCommand
from juicer.command.RPMDeleteCommand import RPMDeleteCommand
from juicer.command.RPMUploadCommand import RPMUploadCommand


class Parser(object):
    def __init__(self):

        self.parser = argparse.ArgumentParser(
            description='Manage release carts')
        juicer.command.parser = self.parser

        self._default_start_in = 're'
        self._default_envs = ['re', 'qa']

        self.parser.add_argument('-v', action='count',
                                 default=1,
                                 help='increase the verbosity (up to 3x)')

        self.parser.add_argument('-V', '--version', action='version',
                                 version='juicer-1.0.0')

        ##################################################################
        # Keep the different commands separate
        subparsers = self.parser.add_subparsers(title='Commands',
                                                dest='command',
                                                description='\'%(prog)s COMMAND -h\' for individual help topics')

        ##################################################################
        # Create the 'cart' sub-parser
        parser_cart = subparsers.add_parser('cart',
                                            help='cart operations')

        subparser_cart = parser_cart.add_subparsers(dest='sub_command')

        ##################################################################
        # Create the 'rpm' sub-parser
        parser_rpm = subparsers.add_parser('rpm',
                                           help='rpm operations')

        subparser_rpm = parser_rpm.add_subparsers(dest='sub_command')

        ##################################################################
        # Create the 'repo' sub-parser
        parser_repo = subparsers.add_parser('repo',
                                            help='repo operations')

        subparser_repo = parser_repo.add_subparsers(dest='sub_command')

        ##################################################################
        # Create the 'cart create' sub-parser
        parser_cart_create = subparser_cart.add_parser('create',
                                                       help='Create a cart with the items specified.',
                                                       usage='%(prog)s CARTNAME [-r REPONAME items ... [ -r REPONAME items ...]]')

        parser_cart_create.add_argument('cartname', metavar='cart-name',
                                        help='Cart name')

        cgroup = parser_cart_create.add_mutually_exclusive_group(required=True)

        cgroup.add_argument('-r', metavar=('reponame', 'item'),
                            action='append',
                            nargs='+',
                            help='Destination repo name')

        parser_cart_create.set_defaults(cmd=CartCreateCommand)

        ##################################################################
        # Create the 'cart show' sub-parser
        parser_cart_show = subparser_cart.add_parser('show',
                                                     usage='%(prog)s CARTNAME [--in [environment [environment ...]]] [-h]',
                                                     help='Print the contents of a cart.')

        parser_cart_show.add_argument('cartname', metavar='name',
                                      help='The name of your cart')

        parser_cart_show.add_argument('--in', nargs='*',
                                      metavar='environment',
                                      default=self._default_envs,
                                      help='Only show carts pushed to the given environment.',
                                      dest='environment')

        parser_cart_show.set_defaults(cmd=CartShowCommand)

        ##################################################################
        # Create the 'cart list' sub-parser
        parser_cart_list = subparser_cart.add_parser('list',
                                                     help='List all of your carts.')

        parser_cart_list.add_argument('cart_glob', metavar='cart_glob',
                                      nargs='*', default=['*'],
                                      help='A pattern to match cart names against (default: *)')

        # parser_cart_list.set_defaults(command=juicer.command.cart_list)

        ##################################################################
        # Create the 'cart update' sub-parser
        parser_cart_update = subparser_cart.add_parser('update',
                                                       help='Update a release cart with items.',
                                                       usage='%(prog)s CARTNAME [-f rpm-manifest] ... [-r REPONAME items ... [-r REPONAME items...]]')

        parser_cart_update.add_argument('cartname', metavar='cartname',
                                        help='The name of your release cart')

        parser_cart_update.add_argument('-r', metavar=('reponame', 'item'),
                                        action='append',
                                        nargs='+',
                                        help='Destination repo name')

        parser_cart_update.add_argument('-f', metavar='rpm-manifest',
                                        action='append',
                                        help='RPM manifest for cart')

        # parser_cart_update.set_defaults(command=juicer.command.cart_update)

        ##################################################################
        # Create the 'cart pull' sub-parser
        parser_cart_pull = subparser_cart.add_parser('pull',
                                                     help='Pull a release cart from remote.')

        parser_cart_pull.add_argument('cartname', metavar='cartname',
                                      help='The name of your release cart')

        # parser_cart_pull.set_defaults(command=juicer.command.cart_pull)

        ##################################################################
        # Create the 'cart push' sub-parser
        parser_cart_push = subparser_cart.add_parser('push',
                                                     help='Pushes/Updates a cart on the pulp server.',
                                                     usage='%(prog)s CARTNAME [--in [environment [environment ...]]] [-h]')

        parser_cart_push.add_argument('cartname', metavar='cartname',
                                      help='The name of your new release cart')

        parser_cart_push.add_argument('--in', nargs='*',
                                      metavar='environment',
                                      default=[self._default_start_in],
                                      help='The environments to push into.',
                                      dest='environment')

        # parser_cart_push.set_defaults(command=juicer.command.cart_push)

        ##################################################################
        # Create the 'cart delete' sub-parser
        parser_cart_delete = subparser_cart.add_parser('delete',
                                                       help='Delete a cart locally and on the pulp server.',
                                                       usage='%(prog)s CARTNAME [-h]')

        parser_cart_delete.add_argument('cartname', metavar='cartname',
                                        help='The name of the release cart to delete')

        parser_cart_delete.set_defaults(cmd=CartDeleteCommand)

        ##################################################################
        # create the 'rpm upload' sub-parser
        parser_rpm_upload = subparser_rpm.add_parser('upload',
                                                     help='Upload the items specified into repos.',
                                                     usage='%(prog)s -r REPONAME items ... [ -r REPONAME items ...] [--in ENV ...]')

        parser_rpm_upload.add_argument('-r', metavar=('reponame', 'item'),
                                       action='append',
                                       nargs='+',
                                       required=True,
                                       help='Destination repo name, items...')

        parser_rpm_upload.add_argument('--in', nargs='*',
                                       metavar='environment',
                                       default=[self._default_start_in],
                                       help='The environments to upload into.',
                                       dest='environment')

        parser_rpm_upload.set_defaults(cmd=RPMUploadCommand)

        ##################################################################
        # create the 'hello' sub-parser
        parser_hello = subparsers.add_parser('hello',
                                             help='test your connection to the pulp server',
                                             usage='%(prog)s [--in env ...]')

        parser_hello.add_argument('--in', nargs='*',
                                  metavar='environment',
                                  help='The environments to test the connection to.',
                                  default=self._default_envs,
                                  dest='environment')

        parser_hello.set_defaults(cmd=HelloCommand)

        ##################################################################
        # create the 'cart promote' sub-parser
        parser_cart_promote = subparser_cart.add_parser('promote',
                                                        help='Promote a cart to the next environment')

        parser_cart_promote.add_argument('cartname', metavar='cart',
                                         help='The name of the cart to promote')

        # parser_cart_promote.set_defaults(command=juicer.command.promote)

        ##################################################################
        # create the 'cart merge' sub-parser
        parser_cart_merge = subparser_cart.add_parser('merge',
                                                      help='Merge the contents of two carts',
                                                      usage='%(prog)s merge CART1 CART2 [CARTN ...]]] --into NEWCART')

        parser_cart_merge.add_argument('carts', nargs="+",
                                       metavar='carts',
                                       help='Two or more carts to merge')

        parser_cart_merge.add_argument('--into', '-i',
                                       metavar='new_cart_name',
                                       help='Name of resultant cart, defaults to updating CART1')

        # parser_cart_merge.set_defaults(command=juicer.command.merge)

        ##################################################################
        # create the 'rpm delete' sub-parser
        parser_rpm_delete = subparser_rpm.add_parser('delete',
                                                     help='Remove rpm(s) from repositories',
                                                     usage='%(prog)s -r REPO-NAME ITEM ITEM ... --in [ENV ...]')

        parser_rpm_delete.add_argument('-r', metavar=('reponame', 'item'),
                                       required=True,
                                       action='append',
                                       nargs='+',
                                       help='Target repo filename, filename...')

        parser_rpm_delete.add_argument('--in', nargs='*',
                                       metavar='environment',
                                       help='The environments to test the connection to',
                                       default=self._default_envs,
                                       dest='environment')

        # parser_rpm_delete.set_defaults(command=juicer.command.delete_rpm)

        ##################################################################
        # Create the 'repo delete' sub-parser
        parser_repo_delete = subparser_repo.add_parser('delete',
                                                       help='Delete pulp repository')

        parser_repo_delete.add_argument('repo', metavar='reponame',
                                        help='Target repo to delete.')

        parser_repo_delete.add_argument('--in', metavar='envs',
                                        nargs="+",
                                        dest='environment',
                                        default=self._default_envs,
                                        help='The environments in which to delete your repository')

        parser_repo_delete.set_defaults(cmd=RepoDeleteCommand)

        ##################################################################
        # create the 'repo publish' sub-parser
        parser_repo_publish = subparser_repo.add_parser('publish',
                                                        help='Publish a repository, this will regenerate metadata.',
                                                        usage='%(prog)s publish REPONAME --in [ENV ...]')

        parser_repo_publish.add_argument('repo', metavar='reponame',
                                         help='Target repo to publish.')

        parser_repo_publish.add_argument('--in', nargs='*',
                                         metavar='environment',
                                         help='The environments to publish repository in.',
                                         default=self._default_envs,
                                         dest='environment')

        parser_repo_publish.set_defaults(cmd=RepoPublishCommand)

        ##################################################################
        # Create the 'repo create' sub-parser
        parser_repo_create = subparser_repo.add_parser('create',
                                                       help='Create pulp repository',
                                                       usage='%(prog)s REPONAME [--feed FEED] [--checksum-type CHECKSUM-TYPE] [--in ENV [...]]')

        parser_repo_create.add_argument('repo', metavar='reponame',
                                        help='The name of your repo')

        parser_repo_create.add_argument('--feed', metavar='feed',
                                        default=None,
                                        help='A feed repo for your repo')

        parser_repo_create.add_argument('--checksum-type', metavar='checksum_type',
                                        default='sha256',
                                        choices=['sha26', 'sha'],
                                        help='Checksum-type used for meta-data generation (one of: sha26, sha)')

        parser_repo_create.add_argument('--in', metavar='environment',
                                        nargs="+",
                                        dest='environment',
                                        default=self._default_envs,
                                        help='The environments in which to create your repository')

        parser_repo_create.set_defaults(cmd=RepoCreateCommand)


def main():  # pragma: no cover
    parser = Parser()
    args = parser.parser.parse_args()
    args.cmd(args).run()

if __name__ == '__main__':  # pragma: no cover
    main()
