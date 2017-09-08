from __future__ import absolute_import, print_function, division
from functools import wraps
from time import sleep
from ..python_libs.colors import bold
from ..env import get_cluster_config
from subprocess import check_call, check_output,getoutput
import os
import sys
import subprocess
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
from msrestazure.azure_exceptions import CloudError
from ..invoke_libs import render
import json
from . import remote
import zipfile

def retry(retries=10, delay=10, backoff=2):
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = retries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except Exception:
                    sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


class Context(object):
    def __init__(self, **kwargs):

        self.__dict__ = kwargs
        self.file = os.path.abspath(self.file)
        self.script = os.path.basename(self.file)
        self.cluster_config = get_cluster_config(self.datacenter)
        self.__dict__.update({
            'project_name': self.file.split(os.sep)[-2],
            'project_path': os.path.dirname(self.file),
            'joara_app_datacenter': self.datacenter,
            'joara_app_main': kwargs.get('joara_app_main', self.cluster_config['JOARA_APP_MAIN']),
            'joara_app_latest': self.cluster_config['JOARA_APP_LATEST'],
            'vault_password': self.cluster_config['VAULT_PASSWORD'],
            'users_path_exists': False,
            'joara_app_docker_registry': self.cluster_config['JOARA_APP_DOCKER_REGISTRY'],
            "datacenter": self.datacenter
        })


        try:
            if ('AZURE_CLIENT_ID' in os.environ and 'AZURE_CLIENT_SECRET' in os.environ and 'AZURE_TENANT_ID' in os.environ and 'AZURE_SUBSCRIPTION_ID' in os.environ):
                self.__dict__.update({
                    'subscription_id': os.environ['AZURE_SUBSCRIPTION_ID'],
                    'client_id': os.environ['AZURE_CLIENT_ID'],
                    'client_secret': os.environ['AZURE_CLIENT_SECRET'],
                    'tenant_id': os.environ['AZURE_TENANT_ID']})
            else:
                self.__dict__.update({
                    'subscription_id': self.cluster_config['AZURE_SUBSCRIPTION_ID'],
                    'client_id': self.cluster_config['AZURE_CLIENT_ID'],
                    'client_secret': self.cluster_config['AZURE_CLIENT_SECRET'],
                    'tenant_id': self.cluster_config['AZURE_TENANT_ID']})

                os.environ['AZURE_CLIENT_ID'] = self.client_id
                os.environ['AZURE_CLIENT_SECRET'] = self.client_secret
                os.environ['AZURE_TENANT_ID'] = self.tenant_id
                os.environ['AZURE_SUBSCRIPTION_ID'] = self.subscription_id
        except Exception as e:
                logs = "### Please update your azure credentials under culsters.ini or to environment variables ###, {}".format(
                    e)
                self.log(logs, fg='red')
                raise RuntimeError(logs)


        self.__dict__.update({
            'key_file': "{}{}".format(self.joara_app_main, self.cluster_config['KEY_FILE']),
            'resource_group_prefix': self.cluster_config['RESOURCE_GROUP_PREFIX'],
            'location': self.cluster_config['LOCATION'],
            'user': self.cluster_config['USER']})

        os.environ['JOARA_APP_LATEST'] = self.cluster_config['JOARA_APP_LATEST']
        os.environ['JOARA_RESOURCE_GROUP_PREFIX'] = self.resource_group_prefix

        self.log("### joara_app_datacenter: {0.joara_app_datacenter} ###".format(self), fg='blue')
        self.resource_group = "{}-{}".format(self.resource_group_prefix, self.datacenter)

        self.credentials = ServicePrincipalCredentials(
            client_id=self.client_id,
            secret=self.client_secret,
            tenant=self.tenant_id
        )

        self.regionmap = {
            "us-west": "westus",
            "us-southcentral": "southcentralus",
            "us-east": "eastus"
        }


        self.client = ResourceManagementClient(self.credentials, self.subscription_id)

        if os.path.exists('/Users'):
            self.users_path_exists = True
        self._app_project_path()

    def __str__(self):
        result = ''
        newline = ''
        for key in self.__dict__:
            result = '{}{}{}: {}'.format(
                result, newline, key, self.__dict__[key])
            newline = '\n'
        return result

    def cd_and_run(self, directory, run_args):
        self.cd(directory)
        self.run('./run --datacenter ' + self.datacenter + ' ' + run_args)

    def cd(self, directory, fg='green'):
        while True:
            prev = directory
            directory = directory.format(self)
            if prev == directory:
                break
        self.log('cd {}'.format(directory), fg='green')
        os.chdir(directory)

    def log(self, msg, fg='yellow'):
        sys.stderr.write(bold(msg + '\n', fg=fg))

    @retry(retries=5, delay=10, backoff=2)
    def run_with_retry(self, *args, **kwargs):
        self.run(*args, **kwargs)


    def getoutput(self, cmd, fg='green',log=True):
        while True:
            prev = cmd
            cmd = cmd.format(self)
            if prev == cmd:
                break

        if log:
            self.log(cmd, fg=fg)
        getoutput(cmd)

    def run(self, cmd, fg='green',log=True):
        while True:
            prev = cmd
            cmd = cmd.format(self)
            if prev == cmd:
                break

        if log:
            self.log(cmd, fg=fg)
        check_call(cmd, shell=True)

    def configure(self):
        if self.group == "jenkins":
            self.sshclient = remote.sshclient("joara-release-jenkins.{location}.cloudapp.azure.com".format(location=self.regionmap[self.location]), "joarajenkins")

            zipf = zipfile.ZipFile('ansible-jenkins.zip', 'w', zipfile.ZIP_DEFLATED)
            self.sshclient.zipdir("{}/infrastructure/configure/jenkins/ansible-jenkins".format(self.joara_app_main), zipf)
            zipf.close()

            self.sshclient.sendCommand("sudo rm -rf /tmp/*")
            self.sshclient.sendCommand("ls -la /tmp/")
            self.sshclient.copyFile("ansible-jenkins.zip")
            self.sshclient.copyFile("{}/infrastructure/configure/jenkins/configure.sh".format(self.joara_app_main))
            self.sshclient.sendCommand("ls -la /tmp/")
            #self.sshclient.sendCommand("eval \"$(ps aux | grep -ie configure.sh  | awk '{print \"kill -9 \" $2}')\"")
            self.log("### Started configuring jenkins ###", fg='blue')
            self.sshclient.sendCommand("chmod +x /tmp/configure.sh ; cd /tmp/ ; ./configure.sh ")

            os.remove("ansible-jenkins.zip")
            self.log("### Completed configuring jenkins ###", fg='blue')

        if self.group == "pre-jenkins":
            self.sshclient = remote.sshclient("joara-release-jenkins.{location}.cloudapp.azure.com".format(location=self.regionmap[self.location]), "joarajenkins")
            self.log("### Getting Jenkins admin credentials ###", fg='blue')
            self.sshclient.sendCommand("sudo cat /var/lib/jenkins/secrets/initialAdminPassword")



    def deploy(self, config_dict):
        """Deploy the template to a resource group."""

        # Dict that maps keys of CloudCenter's region names to values of Azure's region names.
        # Used below to control where something is deployed
        self.log("### Starting the deployment: {0.joara_app_datacenter} ... ###".format(self), fg='green')

        try:
            self.client.resource_groups.create_or_update(
                self.resource_group,
                {
                    'location': self.regionmap[self.location]
                }
            )
        except CloudError as err:
            self.log("CloudError: {0}".format(err), fg='red')
            sys.exit(1)
        except Exception as err:
            self.log("Exception: {0}".format(err), fg='red')
            sys.exit(1)

        try:
            template_path = os.path.join(self.app_project_path, 'templates', 'template.json')
            with open(template_path, 'r') as template_file_fd:
                template = json.load(template_file_fd)
        except Exception as err:
            self.log("Error loading the ARM Template: {0}. Check your syntax".format(err), fg='red')
            sys.exit(1)

        try:
            parameters_path = os.path.join(self.app_project_path, 'templates', 'parameters.json')
            with open(parameters_path, 'r') as armparams_file_fd:
                parameters = armparams_file_fd.read()
        except Exception as err:
            self.log("Error loading the ARM Parameters File: {0}. Check your syntax".format(err), fg='red')
            sys.exit(1)

        attributes = {
            "datacenter": self.datacenter,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        if 'sshkey' in str(parameters):
            pub_ssh_key_path = os.path.expanduser('{user}/.ssh/id_rsa.pub'.format(user=os.path.expanduser("~")))
            with open(pub_ssh_key_path, 'r') as pub_ssh_file_fd:
                sshkey = pub_ssh_file_fd.read()
                attributes.update({
                    "sshkey": sshkey.strip()})

        attributes.update(config_dict)
        parameters = render(str(parameters), attributes)
        parameters = json.loads(str(parameters).replace("'", '"').replace("False", "false"))

        parameters = parameters['parameters']
        deployment_properties = {
            'mode': DeploymentMode.incremental,
            'template': template,
            'parameters': parameters
        }
        try:
            deployment_async_operation = self.client.deployments.create_or_update(
                self.resource_group,
                'joara-resource',
                deployment_properties
            )

            result = deployment_async_operation.result()
            msg = "Deployment completed. Outputs:"
            for k, v in result.properties.outputs.items():
                msg += f"\n- {k} = {str(v['value'])}"
            self.log(msg, fg='yellow')
        except CloudError as err:
            self.log("CloudError: {0}".format(err), fg='red')
            sys.exit(1)
        except Exception as err:
            self.log("Exception: {0}".format(err), fg='red')
            sys.exit(1)

        self.log("### Completed the deployment: {0.joara_app_datacenter} ... ###".format(self), fg='green')

    def destroy(self):
        """Destroy the given resource group"""
        self.log("### Deleting resource group: {0.joara_app_datacenter} ... ###".format(self), fg='green')
        try:
            self.client.resource_groups.delete(self.resource_group)
        except CloudError as err:
            self.log("CloudError: {0}".format(err), fg='red')
            sys.exit(1)
        except Exception as err:
            self.log("Exception: {0}".format(err), fg='red')
            sys.exit(1)

        self.log("### Completed deleting: {0.joara_app_datacenter} ... ###".format(self), fg='green')

    @retry(retries=5, delay=10, backoff=2)
    def invoke_with_retry(self, fg='green'):
        self.invoke(fg)

    def invoke(self, fg='green'):
        cmd = 'GIT_DIR={0.joara_app_main}/.git invoke '

        if 'task' in self.__dict__ and self.task:
            cmd += 'tasks.{0.task} '
        else:
            cmd += 'tasks.all '

        cmd += '--datacenter={} '.format(self.datacenter)

        if 'evars' in self.__dict__ and self.evars:
            cmd += "--extra-vars {0.evars} "

        self.run(cmd)

    def _app_project_path(self):
        xs = self.project_path.split('/')
        self.app_project_path = ''
        include = False
        for x in xs:
            if include:
                self.app_project_path = '{}/{}'.format(
                    self.app_project_path, x)
            if x == 'joara-main':
                include = True
        self.app_project_path = '{}{}'.format(
            self.joara_app_main, self.app_project_path)

    def cd_project(self):
        self.cd(self.app_project_path)

    def copy_project(self):
        self.cd_project()
        self.run('cp -rL ../{0.project_name} /tmp')
        self.cd('/tmp/{0.project_name}')

    def copy_sub_project(self, sub_project):
        self.cd(self.app_project_path + '/' + sub_project)
        self.run('cp -rL ../{} /tmp'.format(sub_project))
        self.cd('/tmp/{}'.format(sub_project))
