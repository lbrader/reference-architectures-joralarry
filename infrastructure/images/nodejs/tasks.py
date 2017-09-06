from invoke import Collection
from joara_app_provision.invoke_libs.kube import tasks
ns = Collection()
ns.add_collection(tasks)


def post(self, attrs):


    attrs.update({
        "image": 'nodejs',
        "port": "3000"

    })
    attrs['flatten'] = False
    return attrs

tasks.Hook.post = post
