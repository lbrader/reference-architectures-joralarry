from __future__ import absolute_import, print_function
from invoke import task
from ..image import Image
from . import KubeApi
from ..decorator import with_context, Hook


@task
@with_context(Hook)
def build(ctx, datacenter):
    image = Image(**ctx.attributes)
    image.build()

@task
@with_context(Hook)
def push(ctx, datacenter):
    if datacenter != 'jenkins':
        image = Image(**ctx.attributes)
        image.push()


@task
@with_context(Hook)
def deploy(ctx, datacenter):
    kube = KubeApi(datacenter=datacenter, **ctx.attributes)
    kube.deploy()

@task
@with_context(Hook)
def scale(ctx, datacenter):
    kube = KubeApi(datacenter=datacenter, **ctx.attributes)
    kube.scale()

@task
@with_context(Hook)
def patch(ctx, datacenter):
    kube = KubeApi(datacenter=datacenter, **ctx.attributes)
    kube.patch()

@task
@with_context(Hook)
def delete(ctx, datacenter):
    kube = KubeApi(datacenter=datacenter, **ctx.attributes)
    kube.delete()

@task
@with_context(Hook)
def all(ctx, datacenter):
    build(ctx, datacenter)
    push(ctx, datacenter)
    deploy(ctx, datacenter)
