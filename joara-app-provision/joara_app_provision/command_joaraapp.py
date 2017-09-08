#!/usr/bin/env python
from __future__ import absolute_import, print_function, division
from .commands.bootstrap_command import bootstrap_add_subcommand, bootstrap_subcommand
from .commands.sync_command import sync_image_add_subcommand, sync_subcommand
from .commands.configure_command import configure_add_subcommand, configure_subcommand
from .commands.image_command import image_add_subcommand, image_subcommand
from .commands.destroy_command import destroy_add_subcommand, destroy_subcommand
import argparse


def main():
    """Main entry point into the provisioning script
    """

    parser = argparse.ArgumentParser(description="Run script to provision JOARA-APP")

    datacenters = ["jenkins","dev", "test", "prod"]
    parser.add_argument(
        "-d", "--datacenter",
        type=str,
        required=False,
        choices=datacenters,
        default="dev",
        help="Where to apply the run script"
    )

    subparsers = parser.add_subparsers(dest='cmd', help='')

    configure_add_subcommand(subparsers)
    bootstrap_add_subcommand(subparsers)
    sync_image_add_subcommand(subparsers)
    image_add_subcommand(subparsers)
    destroy_add_subcommand(subparsers)
    args = parser.parse_args()

    if args.datacenter is None:
        raise RuntimeError('Please specify datacenter ({})'.format(datacenters))


    elif args.cmd == 'bootstrap':
        bootstrap_subcommand(args)
    elif args.cmd == 'image':
        image_subcommand(args)
    elif args.cmd == 'destroy':
        destroy_subcommand(args)
    elif args.cmd == 'configure':
        configure_subcommand(args)
    elif args.cmd == 'syncimage':
        sync_subcommand(args)
    else:
        raise RuntimeError('Unknown subcommand {}'.format(args.cmd))
