
from __future__ import absolute_import, print_function, division
from ..python_libs.context import Context
from ..python_libs.utils import find_joara_app_main
import os



def provision_images(module, images,  args):

    joara_app_main = find_joara_app_main()
    run_file = os.path.join(joara_app_main, module)
    context = Context(file=run_file, task=args.task, evars=args.evars, datacenter=args.datacenter)
    for image in images:
        context.copy_sub_project(image)
        if args.retry:
            context.invoke_with_retry()
        else:
            context.invoke()



def provision(args):
    joara_app_main = find_joara_app_main()
    moudle_path = os.path.join(joara_app_main, 'infrastructure', 'provisioning',args.group,'run')

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


def configure(args):
    joara_app_main = find_joara_app_main()
    if 'jenkins' in args.group:
        moudle_path = os.path.join(joara_app_main, 'infrastructure', 'configure','jenkins','run')
    context = Context(
        file=moudle_path,
        datacenter=args.datacenter,
        group=args.group
    )
    context.copy_project()
    context.configure()


def destroy(args):
    joara_app_main = find_joara_app_main()
    moudle_path = os.path.join(joara_app_main, 'infrastructure', 'provisioning', args.group, 'run')
    context = Context(file=moudle_path, datacenter=args.datacenter,action=args.action)
    context.destroy()

