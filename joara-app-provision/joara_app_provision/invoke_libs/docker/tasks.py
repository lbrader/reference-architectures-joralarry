from __future__ import absolute_import, print_function
from invoke import task
from ...invoke_libs.image import Image
from ...invoke_libs.decorator import with_context, Hook


@task
@with_context(Hook)
def build(ctx, datacenter):
    image = Image(**ctx.attributes)
    image.build()


@task
@with_context(Hook)
def push(ctx, datacenter):
    if datacenter != 'local':
        image = Image(**ctx.attributes)
        image.push()

@task
@with_context(Hook)
def copy(ctx, datacenter):
    if datacenter != 'local':
        image = Image(**ctx.attributes)
        image.copy()

@task
@with_context(Hook)
def remove(ctx, datacenter):
        image = Image(**ctx.attributes)
        image.remove()

@task
@with_context(Hook)
def all(ctx, datacenter):
    build(ctx, datacenter)
    push(ctx, datacenter)
