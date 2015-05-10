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
from juicer.parser.PromptAction import PromptAction

from juicer.command.cart.CartCreateCommand import CartCreateCommand
from juicer.command.cart.CartDeleteCommand import CartDeleteCommand
from juicer.command.cart.CartListCommand import CartListCommand
from juicer.command.cart.CartPullCommand import CartPullCommand
from juicer.command.cart.CartPushCommand import CartPushCommand
from juicer.command.cart.CartShowCommand import CartShowCommand
from juicer.command.cart.CartUpdateCommand import CartUpdateCommand

from juicer.command.HelloCommand import HelloCommand

from juicer.command.repo.RepoCreateCommand import RepoCreateCommand
from juicer.command.repo.RepoDeleteCommand import RepoDeleteCommand
from juicer.command.repo.RepoListCommand import RepoListCommand
from juicer.command.repo.RepoPublishCommand import RepoPublishCommand
from juicer.command.repo.RepoShowCommand import RepoShowCommand

from juicer.command.rpm.RPMDeleteCommand import RPMDeleteCommand
from juicer.command.rpm.RPMUploadCommand import RPMUploadCommand

from juicer.command.role.RoleAddCommand import RoleAddCommand
from juicer.command.role.RoleListCommand import RoleListCommand

from juicer.command.user.UserCreateCommand import UserCreateCommand
from juicer.command.user.UserDeleteCommand import UserDeleteCommand
from juicer.command.user.UserListCommand import UserListCommand
from juicer.command.user.UserShowCommand import UserShowCommand
from juicer.command.user.UserUpdateCommand import UserUpdateCommand

import logging


class Parser(object):
    def __init__(self):

        self.parser = argparse.ArgumentParser(
            description='Manage release carts')
        juicer.command.parser = self.parser

        self._default_start_in = 're'
        self._default_envs = ['re', 'qa']

        self.parser.add_argument('-v', action='store_true',
                                 default=False,
                                 help='show verbose output')

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
        # Create the 'role' sub-parser
        parser_role = subparsers.add_parser('role',
                                            help='role operations')

        subparser_role = parser_role.add_subparsers(dest='sub_command')

        ##################################################################
        # Create the 'user' sub-parser
        parser_user = subparsers.add_parser('user',
                                            help='user operations')

        subparser_user = parser_user.add_subparsers(dest='sub_command')

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

        parser_cart_list.set_defaults(cmd=CartListCommand)

        ##################################################################
        # Create the 'cart update' sub-parser
        parser_cart_update = subparser_cart.add_parser('update',
                                                       help='Update a release cart with items.',
                                                       usage='%(prog)s CARTNAME [-r REPONAME items ... [-r REPONAME items...]]')

        parser_cart_update.add_argument('cartname', metavar='cartname',
                                        help='The name of your release cart')

        parser_cart_update.add_argument('-r', metavar=('reponame', 'item'),
                                        action='append',
                                        nargs='+',
                                        help='Destination repo name')

        parser_cart_update.set_defaults(cmd=CartUpdateCommand)

        ##################################################################
        # Create the 'cart pull' sub-parser
        parser_cart_pull = subparser_cart.add_parser('pull',
                                                     help='Pull a release cart from remote.')

        parser_cart_pull.add_argument('cartname', metavar='cartname',
                                      help='The name of your release cart')

        parser_cart_pull.set_defaults(cmd=CartPullCommand)

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

        parser_cart_push.set_defaults(cmd=CartPushCommand)

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

        ##################################################################
        # Create the 'repo list' sub-parser
        parser_repo_list = subparser_repo.add_parser('list',
                                                     help='List all repos')

        parser_repo_list.add_argument('--in', metavar='envs',
                                      nargs="+",
                                      dest='environment',
                                      default=self._default_envs,
                                      help='The environments in which to list repos')

        parser_repo_list.add_argument('--json',
                                      action='store_true', default=False,
                                      help='Dump everything in JSON format')

        parser_repo_list.set_defaults(cmd=RepoListCommand)

        ##################################################################
        # Create the 'repo show' sub-parser

        parser_repo_show = subparser_repo.add_parser('show',
                                                     usage='%(prog)s REPONAME [...] [--json] --in [ENV ...]',
                                                     help='Show pulp repository(s)')

        parser_repo_show.add_argument('repo', metavar='reponame',
                                      nargs="+",
                                      help='The name of your repo(s)')

        parser_repo_show.add_argument('--json',
                                      action='store_true', default=False,
                                      help='Dump everything in JSON format')

        parser_repo_show.add_argument('--in', metavar='envs',
                                      nargs="+",
                                      dest='environment',
                                      default=self._default_envs,
                                      help='The environments in which to show your repository')

        parser_repo_show.set_defaults(cmd=RepoShowCommand)

        ##################################################################
        # Create the 'role add' sub-parser
        parser_role_add = subparser_role.add_parser('add',
                                                    help='Add user to role')

        parser_role_add.add_argument('--login', metavar='login',
                                     help='Login user id for user',
                                     required=True)

        parser_role_add.add_argument('--role', metavar='role',
                                     help='Role to add user to',
                                     required=True)

        parser_role_add.add_argument('--in', metavar='envs',
                                     nargs="+",
                                     dest='environment',
                                     default=self._default_envs,
                                     help='The environments in which to add user to role')

        parser_role_add.set_defaults(cmd=RoleAddCommand)

        ##################################################################
        # Create the 'role list' sub-parser
        parser_role_list = subparser_role.add_parser('list',
                                                     help='List all roles')

        parser_role_list.add_argument('--in', metavar='envs',
                                      nargs="+",
                                      dest='environment',
                                      default=self._default_envs,
                                      help='The environments in which to list roles')

        parser_role_list.set_defaults(cmd=RoleListCommand)

        ##################################################################
        # Create the 'user create' sub-parser
        parser_user_create = subparser_user.add_parser('create',
                                                       help='Create pulp user',
                                                       usage='%(prog)s LOGIN --name FULLNAME --password PASSWORD \
                       \n\nYou will be prompted if the PASSWORD argument not supplied.')

        parser_user_create.add_argument('login', metavar='login',
                                        help='Login user id for user')

        parser_user_create.add_argument('--name', metavar='name',
                                        dest='name',
                                        required=True,
                                        default=None,
                                        help='Full name of user')

        parser_user_create.add_argument('--password', metavar='password',
                                        dest='password',
                                        nargs='*',
                                        required=True,
                                        action=PromptAction,
                                        help='Plain text password for user')

        parser_user_create.add_argument('--roles', metavar='roles',
                                        nargs="+",
                                        dest='roles',
                                        required=False,
                                        default=None,
                                        help='Roles to apply to the user.')

        parser_user_create.add_argument('--in', metavar='envs',
                                        nargs="+",
                                        dest='environment',
                                        default=self._default_envs,
                                        help='The environments in which to create pulp user')

        parser_user_create.set_defaults(cmd=UserCreateCommand)

        ##################################################################
        # Create the 'user delete' sub-parser
        parser_user_delete = subparser_user.add_parser('delete',
                                                       help='Delete pulp user')

        parser_user_delete.add_argument('login', metavar='login',
                                        help='Login user id for user')

        parser_user_delete.add_argument('--in', metavar='envs',
                                        nargs="+",
                                        dest='environment',
                                        default=self._default_envs,
                                        help='The environments in which to delete user')

        parser_user_delete.set_defaults(cmd=UserDeleteCommand)

        ##################################################################
        # Create the 'user show' sub-parser
        parser_user_show = subparser_user.add_parser('show',
                                                     usage='%(prog)s LOGIN --in [ENV ...]',
                                                     help='Show pulp user')

        parser_user_show.add_argument('login', metavar='login',
                                      help='Login user id for user')

        parser_user_show.add_argument('--in', metavar='envs',
                                      nargs="+",
                                      dest='environment',
                                      default=self._default_envs,
                                      help='The environments in which to show user')

        parser_user_show.set_defaults(cmd=UserShowCommand)

        ##################################################################
        # Create the 'user update' sub-parser
        parser_user_update = subparser_user.add_parser('update',
                                                       help='Change user information',
                                                       usage='%(prog)s LOGIN --name FULLNAME --password PASSWORD \
                       \n\nYou will be prompted if the PASSWORD argument not supplied.')

        parser_user_update.add_argument('login', metavar='login',
                                        help='Login user id for user to update')

        parser_user_update.add_argument('--name', metavar='name',
                                        dest='name',
                                        required=False,
                                        help='Updated name of user')

        parser_user_update.add_argument('--password', metavar='password',
                                        dest='password',
                                        nargs='*',
                                        required=False,
                                        action=PromptAction,
                                        help='Updated password for user')

        parser_user_update.add_argument('--roles', metavar='roles',
                                        nargs="+",
                                        dest='roles',
                                        required=False,
                                        default=None,
                                        help='Roles to apply to the user.')

        parser_user_update.add_argument('--in', metavar='envs',
                                        nargs="+",
                                        dest='environment',
                                        default=self._default_envs,
                                        help='The environments in which to create pulp user')

        parser_user_update.set_defaults(cmd=UserUpdateCommand)

        ##################################################################
        # Create the 'user list' sub-parser
        parser_user_list = subparser_user.add_parser('list',
                                                     help='List all users')

        parser_user_list.add_argument('--in', metavar='envs',
                                      nargs="+",
                                      dest='environment',
                                      default=self._default_envs,
                                      help='The environments in which to list users')

        parser_user_list.set_defaults(cmd=UserListCommand)


def main():  # pragma: no cover

    ######################################################################
    parser = Parser()
    args = parser.parser.parse_args()

    ######################################################################
    # Create the logger object. Right now it is useless, we have no
    # handlers or formatters configurd

    log_level = logging.DEBUG if args.v else logging.INFO
    juicer_logger = logging.getLogger('juicer')
    juicer_logger.setLevel(log_level)

    ######################################################################
    # Now create the stdout 'stream' handler for printing to the
    # console
    juicer_stream_handler = logging.StreamHandler()
    # More items you can put into log records are here:
    # https://docs.python.org/2/library/logging.html#logrecord-attributes
    # We will use message for now. TODO: Add time or other items to debug output.
    # log_string = "%(asctime)s - %(message)s"
    log_string = "%(message)s"
    juicer_stream_formatter = logging.Formatter(log_string)
    juicer_stream_handler.setFormatter(juicer_stream_formatter)
    juicer_stream_handler.setLevel(log_level)

    ######################################################################
    # We have a stream handler, and it has a formatting string set,
    # now we join all the things together
    juicer_logger.addHandler(juicer_stream_handler)
    juicer_logger.debug("initialized juicer-logging at level: %s" % log_level)

    ######################################################################
    args.cmd(args).run()

if __name__ == '__main__':  # pragma: no cover
    main()
