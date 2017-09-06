from __future__ import absolute_import, print_function, division
from ..commands import from_base


def configure_add_subcommand(parser):
    subcommand = parser.add_parser('configure')
    subcommand.add_argument(
        '--group',
        required=True,
        type=str,
        choices=[
            'jenkins',
            'pre-jenkins',
            'git'
        ],
        help="Which module to configure. "
    )

    subcommand.add_argument(
        "-e", "--evars",
        type=str,
        required=False,
        help=""
    )

    subcommand.add_argument(
        "-r", "--retry",
        required=False,
        action="store_true",
        help=""
    )

    return subcommand


def configure_subcommand(args):
    from_base.configure(args)

