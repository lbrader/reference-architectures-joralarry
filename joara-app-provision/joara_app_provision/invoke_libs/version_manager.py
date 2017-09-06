import os
from distutils.util import strtobool
import yaml
from shutil import copyfile
from invoke import run

from colorama import Fore, Back, Style, init

init(autoreset=True, strip=False, convert=False)


class VersionManager(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    def get_latest_image_dict(self, datacenter='local'):
        ifolderpath = os.path.join(self.joara_app_main, 'infrastructure', 'images_version')
        fnamelatest = os.path.join(ifolderpath, 'images_{}.yml'.format(datacenter))
        try:
            if datacenter != 'local' and strtobool(self.attributes['cluster_config']['JOARA_APP_LATEST']):
                cmd = "az storage blob download --container-name imagesversion --file {}/images_{datacenter}.yml --name images_{datacenter}.yml".format(
                    ifolderpath, datacenter=self.datacenter)
                run(cmd, echo=True)
        except:
            pass

        with open(fnamelatest) as f:
            imagedict = yaml.load(f)

        if self.attributes['deploy'] == True and self.attributes['image'] not in imagedict:
            raise RuntimeError(
                Fore.RED + "ERROR: Requested image: {} details are not exist in image inventory \n "
                           "please add the image details to all images_{}.yml file under provisioning/images_version".format(
                    self.attributes['image'], datacenter))

        if imagedict and self.attributes['image'] in imagedict:
            imagedict = imagedict[self.attributes['image']]
            return imagedict
        else:
            dic = {}
            dicitem = {}
            dicitem["base_image_fqdi"] = "{{ base_image_fqdi }}"
            dicitem["branch"] = "{{ branch }}"
            dicitem["build_hostname"] = "{{ build_hostname }}"
            dicitem["build_ip_address"] = "{{ build_ip_address }}"
            dicitem["comment"] = ""
            dicitem["commit"] = "{{ commit }}"
            dicitem["depends_on_image"] = "{{ depends_on_image }}"
            dicitem["environment"] = "{{ environment }}"
            dicitem["image"] = self.attributes['image']
            dicitem["move"] = False if 'move' not in self.attributes else  self.attributes['move']
            dicitem["pull_master_latest"] = False
            dicitem["registry"] = self.attributes['cluster_config']['JOARA_APP_DOCKER_REGISTRY']
            dicitem["use_latest"] = self.attributes['use_latest'] if 'use_latest' in self.attributes else False
            dicitem["user"] = self.attributes['user']
            dicitem["version"] = "{{ version }}"
            dicitem['container_category'] = self.attributes[
                'container_category'] if 'container_category' in self.attributes else "none"
            dic[self.attributes['image']] = dict()
            dic[self.attributes['image']].update(dicitem)
            with   open(fnamelatest, 'a') as f:
                yaml.dump(dic, f, default_flow_style=False)
            return dicitem

    def copyfromstroage(self, datacenter='local'):
        ifolderpath = os.path.join(self.joara_app_main, 'infrastructure', 'images_version')
        fnamelatest = os.path.join(ifolderpath, 'images_{}.yml'.format(datacenter))
        try:
            if datacenter != 'local' and strtobool(self.attributes['cluster_config']['JOARA_APP_LATEST']):
                cmd = "az storage blob download --container-name imagesversion --file {}/images_{datacenter}.yml --name images_{datacenter}.yml".format(
                    ifolderpath, datacenter=self.datacenter)
                run(cmd, echo=True)
        except:
            pass

    def update_images_yaml(self, datacenter='local', **kwdic):
        fname = os.path.join(self.joara_app_main, 'joara-app-provision', 'images.yml')
        fnamelatest = os.path.join(self.joara_app_main, 'infrastructure', 'images_version',
                                   'images_{}.yml'.format(datacenter))
        if not os.path.isfile(fnamelatest):
            copyfile(fname, fnamelatest)

        with open(fnamelatest) as f:
            newdct = yaml.load(f)

        if not newdct:
            newdct = {}

        newdct[kwdic['image']] = kwdic

        with open(fnamelatest, "w") as f:
            yaml.dump(newdct, f, default_flow_style=False)

        if datacenter != 'local':
            fnamelatest = os.path.join(self.joara_app_main, 'infrastructure',  'images_version')
            cmd = "az storage blob upload -f {}/images_{datacenter}.yml -c imagesversion -n images_{datacenter}.yml".format(
                fnamelatest, datacenter=self.datacenter)
            run(cmd, echo=True)

    def get_images_list(self, datacenter='local'):
        ifolderpath = os.path.join(self.joara_app_main, 'infrastructure', 'images_version')
        fnamelatest = os.path.join(ifolderpath, 'images_{}.yml'.format(datacenter))
        with open(fnamelatest) as f:
            dict = yaml.load(f)
        for key in dict.keys():
            yield key

    def get_latest_image_sync_dict(self, image, datacenter='local'):
        ifolderpath = os.path.join(self.joara_app_main, 'infrastructure', 'images_version')
        self.fnamelatest = os.path.join(ifolderpath, 'images_{}.yml'.format(datacenter))
        with open(self.fnamelatest) as f:
            dict = yaml.load(f)
        try:
            dict = dict[image]
        except:
            print(Fore.RED + 'ERROR: Image {} not exist'.format(image))
            return {}
        return dict
