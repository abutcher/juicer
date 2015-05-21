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
import logging

import juicer.command.cart
import juicer.command.hello
import juicer.command.repo
import juicer.command.rpm
import juicer.command.role
import juicer.command.user
import juicer.parser
from juicer.parser.PromptAction import PromptAction


class Parser(object):
    def __init__(self):

        self.parser = argparse.ArgumentParser(
            description='manage pulp and release carts')
        juicer.command.parser = self.parser

        self._default_start_in = 're'
        self._default_envs = ['re', 'qa']

        self.parser.add_argument('-v', '--verbose', action='store_true',
                                 dest='verbose',
                                 default=False,
                                 help='show verbose output')

        self.parser.add_argument('-V', '--version', action='version',
                                 version='juicer-1.0.0')

        ##################################################################
        # Keep the different commands separate
        subparsers = self.parser.add_subparsers(title='commands',
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
                                                       help='create cart with destination repositories and items',
                                                       usage='%(prog)s CARTNAME [-r REPONAME ITEM ... [-r REPONAME ITEM ...]] [-h]')

        parser_cart_create.add_argument('cartname', metavar='CARTNAME',
                                        help='cart name')

        cgroup = parser_cart_create.add_mutually_exclusive_group(required=True)

        cgroup.add_argument('-r', metavar=('REPONAME', 'ITEM'),
                            action='append',
                            nargs='+',
                            help='destination repo name, items')

        parser_cart_create.set_defaults(cmd=juicer.command.cart.CartCreateCommand)

        ##################################################################
        # Create the 'cart show' sub-parser
        parser_cart_show = subparser_cart.add_parser('show',
                                                     usage='%(prog)s CARTNAME [-h]',
                                                     help='show the contents of a cart')

        parser_cart_show.add_argument('cartname', metavar='CARTNAME',
                                      help='cart name')

        parser_cart_show.set_defaults(cmd=juicer.command.cart.CartShowCommand)

        ##################################################################
        # Create the 'cart list' sub-parser
        parser_cart_list = subparser_cart.add_parser('list',
                                                     usage='%(prog)s [GLOB] [-h]',
                                                     help='list local carts')

        parser_cart_list.add_argument('cart_glob', metavar='GLOB',
                                      nargs='*', default=['*'],
                                      help='pattern to match cart names against (default: *)')

        parser_cart_list.set_defaults(cmd=juicer.command.cart.CartListCommand)

        ##################################################################
        # Create the 'cart update' sub-parser
        parser_cart_update = subparser_cart.add_parser('update',
                                                       help='update cart with new items',
                                                       usage='%(prog)s CARTNAME [-r REPONAME ITEM ... [-r REPONAME ITEM ...]] [-h]')

        parser_cart_update.add_argument('cartname', metavar='CARTNAME',
                                        help='cart name')

        parser_cart_update.add_argument('-r', metavar=('REPONAME', 'ITEM'),
                                        action='append',
                                        nargs='+',
                                        help='destination repo name, items')

        parser_cart_update.set_defaults(cmd=juicer.command.cart.CartUpdateCommand)

        ##################################################################
        # Create the 'cart pull' sub-parser
        parser_cart_pull = subparser_cart.add_parser('pull',
                                                     usage='%(prog)s CARTNAME [-h]',
                                                     help='pull cart from remote')

        parser_cart_pull.add_argument('cartname', metavar='CARTNAME',
                                      help='cart name')

        parser_cart_pull.set_defaults(cmd=juicer.command.cart.CartPullCommand)

        ##################################################################
        # Create the 'cart push' sub-parser
        parser_cart_push = subparser_cart.add_parser('push',
                                                     help='upload cart items to pulp',
                                                     usage='%(prog)s CARTNAME [--in ENV [ENV ...]] [-h]')

        parser_cart_push.add_argument('cartname', metavar='CARTNAME',
                                      help='cart name')

        parser_cart_push.add_argument('--in', nargs='*',
                                      metavar='ENV',
                                      default=[self._default_start_in],
                                      help='environments to push to',
                                      dest='environment')

        parser_cart_push.set_defaults(cmd=juicer.command.cart.CartPushCommand)

        ##################################################################
        # Create the 'cart delete' sub-parser
        parser_cart_delete = subparser_cart.add_parser('delete',
                                                       help='delete cart locally and on remote',
                                                       usage='%(prog)s CARTNAME [-h]')

        parser_cart_delete.add_argument('cartname', metavar='CARTNAME',
                                        help='cart name')

        parser_cart_delete.set_defaults(cmd=juicer.command.cart.CartDeleteCommand)

        ##################################################################
        # create the 'rpm upload' sub-parser
        parser_rpm_upload = subparser_rpm.add_parser('upload',
                                                     help='upload rpms to repositories',
                                                     usage='%(prog)s -r REPONAME ITEM ... [ -r REPONAME ITEM ...] [--in ENV [ENV ...]] [-h]')

        parser_rpm_upload.add_argument('-r', metavar=('REPONAME', 'ITEM'),
                                       action='append',
                                       nargs='+',
                                       required=True,
                                       help='destination repo name, items...')

        parser_rpm_upload.add_argument('--in', nargs='*',
                                       metavar='ENV',
                                       default=[self._default_start_in],
                                       help='environments to upload to',
                                       dest='environment')

        parser_rpm_upload.set_defaults(cmd=juicer.command.rpm.RPMUploadCommand)

        ##################################################################
        # create the 'hello' sub-parser
        parser_hello = subparsers.add_parser('hello',
                                             help='test your connection to the pulp server',
                                             usage='%(prog)s [--in ENV [ENV ...]]')

        parser_hello.add_argument('--in', nargs='*',
                                  metavar='ENV',
                                  help='environments to test agsint',
                                  default=self._default_envs,
                                  dest='environment')

        parser_hello.set_defaults(cmd=juicer.command.hello.HelloCommand)

        ##################################################################
        # create the 'rpm delete' sub-parser
        parser_rpm_delete = subparser_rpm.add_parser('delete',
                                                     help='delete rpms from repositories',
                                                     usage='%(prog)s -r REPONAME ITEM ... [-r REPONAME ITEM ...] [--in ENV [ENV ...]] [-h]')

        parser_rpm_delete.add_argument('-r', metavar=('REPONAME', 'ITEM'),
                                       required=True,
                                       action='append',
                                       nargs='+',
                                       help='target repo name, items')

        parser_rpm_delete.add_argument('--in', nargs='*',
                                       metavar='ENV',
                                       help='environments to delete from',
                                       default=self._default_envs,
                                       dest='environment')

        parser_rpm_delete.set_defaults(command=juicer.command.rpm.RPMDeleteCommand)

        ##################################################################
        # Create the 'repo delete' sub-parser
        parser_repo_delete = subparser_repo.add_parser('delete',
                                                       usage='%(prog)s REPONAME [--in ENV [ENV ...]] [-h]',
                                                       help='delete a repository')

        parser_repo_delete.add_argument('repo', metavar='REPONAME',
                                        help='repo name')

        parser_repo_delete.add_argument('--in', metavar='ENV',
                                        nargs="+",
                                        dest='environment',
                                        default=self._default_envs,
                                        help='environments to delete from')

        parser_repo_delete.set_defaults(cmd=juicer.command.repo.RepoDeleteCommand)

        ##################################################################
        # create the 'repo publish' sub-parser
        parser_repo_publish = subparser_repo.add_parser('publish',
                                                        help='publish a repository (this will regenerate metadata)',
                                                        usage='%(prog)s REPONAME [-t, --type TYPE] [--in ENV [ENV ...]] [-h]')

        parser_repo_publish.add_argument('repo', metavar='REPONAME',
                                         help='repo name')

        parser_repo_publish.add_argument('-t', '--type', metavar='TYPE',
                                         dest='repotype',
                                         default='rpm',
                                         choices=['rpm', 'docker'],
                                         help='type used for repository publication (one of: rpm, docker)(default: rpm)')

        parser_repo_publish.add_argument('--in', nargs='*',
                                         metavar='ENV',
                                         help='environments to publish in',
                                         default=self._default_envs,
                                         dest='environment')

        parser_repo_publish.set_defaults(cmd=juicer.command.repo.RepoPublishCommand)

        ##################################################################
        # Create the 'repo create' sub-parser
        parser_repo_create = subparser_repo.add_parser('create',
                                                       help='create a repository',
                                                       usage='%(prog)s REPONAME [-t,--type TYPE] [--checksum-type CHECKSUM-TYPE] [--in ENV [ENV ...]] [-h]')

        parser_repo_create.add_argument('repo', metavar='REPONAME',
                                        help='repo name')

        parser_repo_create.add_argument('-t', '--type', metavar='TYPE',
                                        dest='repotype',
                                        default='rpm',
                                        choices=['rpm', 'docker'],
                                        help='type used for repository creation (one of: rpm, docker)(default: rpm)')

        parser_repo_create.add_argument('--checksum-type', metavar='CHECKSUM-TYPE',
                                        default='sha256',
                                        choices=['sha26', 'sha'],
                                        help='checksum-type used for metadata generation (one of: sha26, sha)')

        parser_repo_create.add_argument('--in', metavar='ENV',
                                        nargs="+",
                                        dest='environment',
                                        default=self._default_envs,
                                        help='environments to create in')

        parser_repo_create.set_defaults(cmd=juicer.command.repo.RepoCreateCommand)

        ##################################################################
        # Create the 'repo list' sub-parser
        parser_repo_list = subparser_repo.add_parser('list',
                                                     usage='%(prog)s [--json] [--in ENV [ENV ...]] [-h]',
                                                     help='list repositories')

        parser_repo_list.add_argument('--in', metavar='envs',
                                      nargs="+",
                                      dest='ENV',
                                      default=self._default_envs,
                                      help='environments to list from')

        parser_repo_list.add_argument('--json',
                                      action='store_true', default=False,
                                      help='output json')

        parser_repo_list.set_defaults(cmd=juicer.command.repo.RepoListCommand)

        ##################################################################
        # Create the 'repo show' sub-parser

        parser_repo_show = subparser_repo.add_parser('show',
                                                     usage='%(prog)s REPONAME ... [--json] [--in ENV [ENV ...]] [-h]',
                                                     help='show one or more repositories')

        parser_repo_show.add_argument('repo', metavar='REPONAME',
                                      nargs="+",
                                      help='repo name')

        parser_repo_show.add_argument('--json',
                                      action='store_true', default=False,
                                      help='output json')

        parser_repo_show.add_argument('--in', metavar='ENV',
                                      nargs="+",
                                      dest='environment',
                                      default=self._default_envs,
                                      help='environments to show from')

        parser_repo_show.set_defaults(cmd=juicer.command.repo.RepoShowCommand)

        ##################################################################
        # Create the 'role add' sub-parser
        parser_role_add = subparser_role.add_parser('add',
                                                    usage='%(prog)s --login LOGIN --role ROLE [--in ENV [ENV ...]] [-h]',
                                                    help='add user to role')

        parser_role_add.add_argument('--login', metavar='LOGIN',
                                     help='user\'s login',
                                     required=True)

        parser_role_add.add_argument('--role', metavar='ROLE',
                                     help='role to add user to',
                                     required=True)

        parser_role_add.add_argument('--in', metavar='ENV',
                                     nargs="+",
                                     dest='environment',
                                     default=self._default_envs,
                                     help='environments to add roles in')

        parser_role_add.set_defaults(cmd=juicer.command.role.RoleAddCommand)

        ##################################################################
        # Create the 'role list' sub-parser
        parser_role_list = subparser_role.add_parser('list',
                                                     usage='%(prog)s [--in ENV [ENV ...]] [-h]',
                                                     help='list roles')

        parser_role_list.add_argument('--in', metavar='ENV',
                                      nargs="+",
                                      dest='environment',
                                      default=self._default_envs,
                                      help='environments to list from')

        parser_role_list.set_defaults(cmd=juicer.command.role.RoleListCommand)

        ##################################################################
        # Create the 'user create' sub-parser
        parser_user_create = subparser_user.add_parser('create',
                                                       help='create a user',
                                                       usage='%(prog)s LOGIN --name \"FULL NAME\" [--password [\"PASSWORD\"]] [--roles ROLE ...] [--in ENV [ENV ...]] [-h]')

        parser_user_create.add_argument('login', metavar='LOGIN',
                                        help='login id for user')

        parser_user_create.add_argument('--name', metavar='FULL NAME',
                                        dest='name',
                                        required=True,
                                        default=None,
                                        help='full name')

        parser_user_create.add_argument('--password', metavar='PASSWORD',
                                        dest='password',
                                        nargs='*',
                                        required=True,
                                        action=PromptAction,
                                        help='password (prompted if not argument not supplied)')

        parser_user_create.add_argument('--roles', metavar='ROLE',
                                        nargs="+",
                                        dest='roles',
                                        required=False,
                                        default=None,
                                        help='roles to apply to user (defaults to None)')

        parser_user_create.add_argument('--in', metavar='ENV',
                                        nargs="+",
                                        dest='environment',
                                        default=self._default_envs,
                                        help='environments to create in')

        parser_user_create.set_defaults(cmd=juicer.command.user.UserCreateCommand)

        ##################################################################
        # Create the 'user delete' sub-parser
        parser_user_delete = subparser_user.add_parser('delete',
                                                       usage='%(prog)s LOGIN [--in ENV [ENV ...]] [-h]',
                                                       help='delete a user')

        parser_user_delete.add_argument('login', metavar='LOGIN',
                                        help='login id for user')

        parser_user_delete.add_argument('--in', metavar='ENV',
                                        nargs="+",
                                        dest='environment',
                                        default=self._default_envs,
                                        help='environments to delete from')

        parser_user_delete.set_defaults(cmd=juicer.command.user.UserDeleteCommand)

        ##################################################################
        # Create the 'user show' sub-parser
        parser_user_show = subparser_user.add_parser('show',
                                                     usage='%(prog)s LOGIN [--in ENV [ENV ...]] [-h]',
                                                     help='show a user')

        parser_user_show.add_argument('login', metavar='LOGIN',
                                      help='login id for user')

        parser_user_show.add_argument('--in', metavar='ENV',
                                      nargs="+",
                                      dest='environment',
                                      default=self._default_envs,
                                      help='environments to show from')

        parser_user_show.set_defaults(cmd=juicer.command.user.UserShowCommand)

        ##################################################################
        # Create the 'user update' sub-parser
        parser_user_update = subparser_user.add_parser('update',
                                                       help='change user information',
                                                       usage='%(prog)s LOGIN [--name \"FULL NAME\"] [--password [\"PASSWORD\"]] [--roles ROLE ...] [--in ENV [ENV ...]] [-h]')

        parser_user_update.add_argument('login', metavar='LOGIN',
                                        help='login id for user')

        parser_user_update.add_argument('--name', metavar='FULL NAME',
                                        dest='name',
                                        required=False,
                                        help='updated full name')

        parser_user_update.add_argument('--password', metavar='PASSWORD',
                                        dest='password',
                                        nargs='*',
                                        required=False,
                                        action=PromptAction,
                                        help='updated password (prompted if argument not supplied)')

        parser_user_update.add_argument('--roles', metavar='ROLE',
                                        nargs="+",
                                        dest='roles',
                                        required=False,
                                        default=None,
                                        help='updated roles')

        parser_user_update.add_argument('--in', metavar='ENV',
                                        nargs="+",
                                        dest='environment',
                                        default=self._default_envs,
                                        help='environments to update in')

        parser_user_update.set_defaults(cmd=juicer.command.user.UserUpdateCommand)

        ##################################################################
        # Create the 'user list' sub-parser
        parser_user_list = subparser_user.add_parser('list',
                                                     usage='%(prog)s [--in ENV [ENV ...]] [-h]',
                                                     help='list users')

        parser_user_list.add_argument('--in', metavar='ENV',
                                      nargs="+",
                                      dest='environment',
                                      default=self._default_envs,
                                      help='environments to list from')

        parser_user_list.set_defaults(cmd=juicer.command.user.UserListCommand)


def main():  # pragma: no cover

    ######################################################################
    parser = Parser()
    args = parser.parser.parse_args()

    ######################################################################
    # Create the logger object. Right now it is useless, we have no
    # handlers or formatters configurd

    log_level = logging.DEBUG if args.verbose else logging.INFO
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
