from invoke import Collection
from joara_app_provision.invoke_libs.docker import tasks
ns = Collection()
ns.add_collection(tasks)


def post(self, attrs):
    attrs['image'] = 'alpine'
    attrs['flatten'] = False
    return attrs

tasks.Hook.post = post
