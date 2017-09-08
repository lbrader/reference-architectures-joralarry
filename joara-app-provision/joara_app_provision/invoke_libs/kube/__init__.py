from __future__ import absolute_import, print_function
from ..image import Image
from requests import post, put, get
from json import loads, dumps
from os import environ
from .. import render
from distutils.util import strtobool
from colorama import Fore, Back, Style, init
import yaml
import os
from kubernetes import client, config
from kubernetes.client import api_client
from kubernetes.client.apis import core_v1_api
from ...python_libs.colors import bold
from invoke import run
import sys
from itertools import chain
try:
    from itertools import imap
except ImportError:
    # Python 3...
    imap=map
class KubeApi(object):
    def __init__(self, datacenter, **kwargs):


        self.datacenter = datacenter
        self.image = kwargs['image']
        img = Image(deploy=True, **kwargs)
        self.version = img.current_version()
        user= kwargs["cluster_config"]["JOARA_APP_DOCKER_USER"]

        try:
            os.makedirs("{user}/.kube".format(user=os.path.expanduser("~")), exist_ok=True)
            run(
                "scp  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i {user}/.ssh/id_rsa joaraacs{datacenter}@jora-acs-mgmt-{datacenter}.eastus.cloudapp.azure.com:.kube/config {user}/.kube/config".format(
                    user=os.path.expanduser("~"), datacenter=self.datacenter))
            config.load_kube_config()
            self.apiclient = api_client.ApiClient()
            self.api = core_v1_api.CoreV1Api(self.apiclient)
            self.k8s_beta = client.ExtensionsV1beta1Api()
        except Exception as err:
            self.log("### Error copying Kube config, Exception: {} ### ".format(err), fg='red')
            sys.exit(1)

        attributes = {
            "datacenter": self.datacenter,
            "version": self.version,
            "user": user,
            "replicas": kwargs['count'] if int(kwargs['count']) > 1 else self._getreplica(),
            "name": self.image,
            "registry": kwargs["cluster_config"]["JOARA_APP_DOCKER_REGISTRY"],
            "deploy_app": deployment_app,
            "service_app": service_app
        }
        attributes.update(kwargs)
        self.attributes = attributes
        self.replicas= int(self.attributes["replicas"])


        self.deploy_app = render(attributes['deploy_app'], attributes)
        self.service_app = render(attributes['service_app'], attributes)



    def _getreplica(self):
        count = 1
        try:
            resp = self.k8s_beta.list_namespaced_replica_set(namespace="default")
            for i in resp.items:
                if i.metadata.labels["name"] == self.image:
                    count = int(i.spec.replicas)
                    if count > 0:
                        self.log("### Deployment: {image} already running in datacenter {datacenter} with replica {count} deployed ###".format(
                            image=self.image, datacenter=self.datacenter, count=count), fg='blue')
                        return count
            return count
        except Exception as err:
            self.log("### Error getting replica details: {}. ### ".format(err), fg='red')
            return count

    def _get_ruuning_imageversion(self):
        try:
            resp = self.k8s_beta.list_namespaced_deployment(namespace="default")
            for i in resp.items:
                if i.metadata.name == self.image:
                    deployedimage = i.spec.template.spec.containers[0].image
                    xs = deployedimage.split(':')
                    xs = list(self.flatmap(lambda ys: ys.split('/'), xs))
                    tag = xs.pop()
                    image = xs.pop()
                    self.log("### Deployment: {image} already running in datacenter {datacenter} with image name {deployedimage} deployed ###".format(
                            image=self.image, datacenter=self.datacenter, deployedimage=deployedimage), fg='blue')
                    return tag
            return "Not Found"
        except Exception as err:
            self.log("### Error getting ruuning details: {}. ### ".format(err), fg='red')
            return "Not Found"

    def deploy(self):
        try:
             dep = yaml.load(self.deploy_app)
             if not self._is_deployment_deployed():
                 resp = self.k8s_beta.create_namespaced_deployment(
                     body=dep, namespace="default")
                 self.log("### Deployment created. status='{}' ### ".format(resp.status), fg='blue')
             else:
                 self.log("### Deployment {} already exist, so it will patch ### ".format(self.image), fg='green')
                 run_version=self._get_ruuning_imageversion()
                 run_replica = int(self._getreplica())
                 self.log("### Deployment compare {run_version}={version} ,{run_replica}={replicas} ### ".format(run_version=run_version.strip(), version=self.version.strip(), run_replica=run_replica,replicas=self.replicas),
                          fg='green')
                 if not "Not Found" in run_version and ( run_version.strip() != self.version.strip() or  run_replica != self.replicas):
                    self.patch()
                 else:
                     self.log("### Deployment {} already exist, with same schema, so patch skipped ### ".format(self.image), fg='green')

             if not self._is_service_deployed():
                 srv = yaml.load(self.service_app)

                 resp = self.api.create_namespaced_service(body=srv,
                                                      namespace="default")
                 self.log("### Service created. status='{}' ### ".format(resp.status), fg='blue')
             else:
                 self.log("### Service {} already exist ### ".format(self.image), fg='green')
        except Exception as err:
            self.log("### Error deployment details: {}. ### ".format(err), fg='red')
            sys.exit(1)

    def scale(self):
        try:
             dep = yaml.load(self.deploy_app)

             if self._is_deployment_deployed():
                 resp=self.k8s_beta.patch_namespaced_deployment_scale(name=self.image, body=dep, namespace="default")
                 self.log("### Scale Deployment created. status='{}' ### ".format(resp.status), fg='blue')
             else:
                 self.log("### Deployment {} not exist ### ".format(self.image), fg='red')
        except Exception as err:
            self.log("### Error scale details: {}. ### ".format(err), fg='red')
            sys.exit(1)

    def delete(self):
        try:
             if self._is_deployment_deployed():
                 resp=self.k8s_beta.delete_collection_namespaced_deployment(namespace="default")
                 self.log("### Delete Deployment created. status='{}' ### ".format(resp.status), fg='blue')
             else:
                 self.log("### Deployment {} not exist ### ".format(self.image), fg='red')

             if self._is_service_deployed():
                 srv = yaml.load(self.service_app)
                 resp = self.api.delete_namespaced_service(name=self.image,namespace="default")
                 self.log("### Delete Service created. status='{}' ### ".format(resp.status), fg='blue')
             else:
                 self.log("### Service {} not exist ### ".format(self.image), fg='green')
        except Exception as err:
            self.log("### Error delete details: {}. ### ".format(err), fg='red')
            sys.exit(1)


    def patch(self):
        try:
             dep = yaml.load(self.deploy_app)
             if self._is_deployment_deployed():
                 resp=self.k8s_beta.patch_namespaced_deployment(name=self.image, body=dep, namespace="default")
                 self.log("### Patch Deployment created. status='{}' ### ".format(resp.status), fg='blue')
             else:
                 self.log("### Deployment {} not exist, Please deploy first ### ".format(self.image), fg='red')
        except Exception as err:
            self.log("### Error patching deployment details: {}. ### ".format(err), fg='red')
            return False

    def log(self, msg, fg='yellow'):
        sys.stderr.write(bold(msg + '\n', fg=fg))

    def _is_deployment_deployed(self):
        try:
            resp = self.k8s_beta.list_namespaced_deployment(namespace="default")
            for i in resp.items:
                if i.metadata.name == self.image:
                    self.log("### Deployment: {deployment} deployed ###".format(deployment=self.image), fg='blue')
                    return True
            return False
        except Exception as err:
            self.log("### Error getting deployment details: {}. ### ".format(err), fg='red')
            return False

    def get(self):
        try:
            resp = self.k8s_beta.list_namespaced_deployment(namespace="default")
            for i in resp.items:
                if i.metadata.name == self.image:
                    self.log("### Deployment Details: {deployment} ###".format(deployment=i), fg='blue')
                    return True

            self.log("### Deployment Details: {image} doesn't exist ###".format(image=self.image), fg='blue')
            return False
        except Exception as err:
            self.log("### Error getting deployment details: {}. ### ".format(err), fg='red')
            return False

    def flatmap(self,f, items):
        return chain.from_iterable(imap(f, items))

    def _is_service_deployed(self):
        try:
            resp = self.api.list_namespaced_service(namespace="default")
            self.log("### Service details. status='{}' ### ".format(resp), fg='blue')
            for i in resp.items:
                if i.metadata.name == self.image:
                    self.log("### Service: {service} running @ip: {ip} ###".format(service=self.image,ip=i.status.load_balancer.ingress[0].ip), fg='blue')
                    return True
            return False
        except Exception as err:
            self.log("###  Error getting service details: {}. ### ".format(err), fg='red')
            return False


deployment_app = """
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: {{ image }}
spec:
  replicas: {{ replicas }}
  template:
    metadata:
      labels:
        name: {{ image }}
    spec:
      containers:
      - image: {{ registry }}/{{ user }}/{{ image }}:{{ version }}
        name: {{ image }}
        imagePullPolicy: Always
        ports:
        - containerPort: {{ port }}
          name: http-server
          
""".strip()

service_app = """
apiVersion: v1
kind: Service
metadata:
  name: {{ image }}
  labels:
    name: {{ image }}
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: {{ port }}
      protocol: TCP
  selector:
    name: {{ image }}
    
""".strip()