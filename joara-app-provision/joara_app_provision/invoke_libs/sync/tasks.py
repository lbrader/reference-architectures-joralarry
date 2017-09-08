from __future__ import absolute_import, print_function
from invoke import task
from ...invoke_libs.sync.copy_docker import CopyDocker
from ...invoke_libs.decorator import with_context, Hook


@task
@with_context(Hook)
def copy(ctx, datacenter):
    if datacenter != 'local':
        copy = CopyDocker(datancenter=datacenter, **ctx.attributes)
        copy.copy()


@task
@with_context(Hook)
def copyimage(ctx, datacenter):
    if datacenter != 'local':
        copy = CopyDocker(datancenter=datacenter, **ctx.attributes)
        copy.copyimage()
