from __future__ import absolute_import, print_function, division
from ..python_libs.context import Context
from ..python_libs.utils import find_joara_app_main
from ..commands import from_base
import os


def destroy_add_subcommand(parser):


    subcommand = parser.add_parser('destroy')

    subcommand.add_argument(
        '--group',
        required=True,
        type=str,
        choices=[
            'jenkins',
            'acr',
            'acs',
            'vm',
            'monitor'
        ],
        help="Which module to destrory"
    )
    subcommand.add_argument(
        '--action',
        type=str,
        choices=[
            'plan-destroy',
            'destroy'
        ],
        nargs='?',
        default='destroy',
        help="Which action to be performed by arm"
    )
    return subcommand


def destroy_subcommand(args):

    from_base.destroy(args)
