from invoke import Collection
from joara_app_provision.invoke_libs.sync import tasks

ns = Collection()
ns.add_collection(tasks)


def post(self, attrs):
    attrs.update({
        "from_datacenter": attrs["source"] if "source" in attrs else "",
        "image": attrs["image"] if "image" in attrs else "",
        "copy_images": attrs["images"] if "images" in attrs else []

    })
    return attrs


tasks.Hook.post = post
