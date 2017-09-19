from __future__ import absolute_import, print_function, division
from ..commands import from_base
from ..log import logging

logger = logging.get_logger(__name__)
def git_add_subcommand(parser):
    subcommand = parser.add_parser('gitconfigure')
    subcommand.add_argument(
        '--group',
        required=True,
        type=str,
        choices=[
            'git'
        ],
        help="Which module to configure. "
    )

    subcommand.add_argument(
        '--image',
        required=True,
        nargs="?",
        type=str,
        help="Which images to configure in git "
    )

    subcommand.add_argument(
        '--task',
        type=str,
        required=True,
        choices=[
            'repo',
            'deleterepo',
            'orghook',
            'repohook',
            'protect',
            'all'
        ],
        help="Which action to be performed on the git repo "
    )

    subcommand.add_argument('--verbose', required=False, action='count', default=True)

    return subcommand


def git_subcommand(args):
    if 'git' in args.group:
        if args.image:
            from_base.configure_git(args)
        else:
            logger.warn("Please provide a image name to configure in git")

