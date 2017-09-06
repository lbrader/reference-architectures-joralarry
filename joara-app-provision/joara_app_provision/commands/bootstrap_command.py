from __future__ import absolute_import, print_function, division
from ..commands import from_base


def bootstrap_add_subcommand(parser):
    subcommand = parser.add_parser('bootstrap')
    subcommand.add_argument(
        '--group',
        required=True,
        type=str,
        choices=[
            'jenkins',
            'acr',
            'acs',
            'vm',
            'storage',
            'monitor'
        ],
        help="Which module to provision, use all to provision everything. "
    )

    subcommand.add_argument(
        '--count',
        type=int,
        default='1',
        help="what is the count of agent nodes"
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


def bootstrap_subcommand(args):
    from_base.provision(args)

