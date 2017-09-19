
from __future__ import absolute_import, print_function, division
from ..python_libs.context import Context
from ..python_libs.utils import find_app_main
import os
import shutil
from ..log import logging
import sys

logger = logging.get_logger(__name__)

def provision_images(module, images,  args):
    app_main = find_app_main()
    run_file = os.path.join(app_main, module)
    context = Context(file=run_file, task=args.task,  datacenter=args.datacenter)
    for image in images:
        context.copy_sub_project(image)
        attributes = {
            "count": args.count
        }
        context.image_action(attributes,args)



def sync_version(run_file, args):
    context = Context(file=run_file, task=args.task,  datacenter=args.datacenter)
    #context.copy_project()
    attributes ={
        "from_datacenter": args.source
    }
    context.sync_action(attributes,args)

def provision(args):
    app_main = find_app_main()
    moudle_path = os.path.join(app_main, 'infrastructure', 'provisioning',args.group,'run')

    if args.group == 'acs':
        attributes = {
            "agentcount": args.count
        }
    else:
        attributes = { }


    context = Context(
        file=moudle_path,
        datacenter=args.datacenter,
        group=args.group
    )
    context.copy_project()
    context.deploy(attributes)
    os.chdir(app_main)


def configure_jenkins(args):
    app_main = find_app_main()
    if 'jenkins' in args.group:
        moudle_path = os.path.join(app_main, 'infrastructure', 'configure','jenkins','run')
    context = Context(
        file=moudle_path,
        datacenter=args.datacenter,
        group=args.group
    )
    try:
        files = ["id_rsa","id_rsa.pub"]
        for file in files:
            shutil.copyfile(os.path.join(os.path.expanduser("~"), ".ssh",file),os.path.join(app_main, 'infrastructure', 'configure','jenkins','ansible-jenkins','roles','jenkins','files','ssh',file))

        logger.info("Completed copying ssh keys for jenkins configuration")
    except Exception as err:
        logger.error("Error copying ssh keys for jenkins configuration at: {0}".format(err))
        sys.exit(1)

    context.copy_project()
    context.configure_jenkins()

def configure_git(args):
    app_main = find_app_main()
    if 'git' in args.group:
        moudle_path = os.path.join(app_main, 'infrastructure', 'images_repo',args.image,'run')
    context = Context(
        file=moudle_path,
        datacenter=args.datacenter,
        group=args.group
    )
    context.copy_project()
    context.configure_git(args)
    os.chdir(app_main)




def destroy(args):
    app_main = find_app_main()
    moudle_path = os.path.join(app_main, 'infrastructure', 'provisioning', args.group, 'run')
    context = Context(file=moudle_path, datacenter=args.datacenter,action=args.action)
    context.destroy()

