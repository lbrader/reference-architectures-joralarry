from paramiko import client
from scp import SCPClient
import zipfile
from os import walk
import os
from ..python_libs.colors import bold
import sys

class sshclient(object):
    client = None

    def __init__(self, address, username):
        self.log("### Connecting to server. ###".format(self), fg='blue')
        self.client = client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        self.client.connect(address, username=username, key_filename='{user}/.ssh/id_rsa'.format(user=os.path.expanduser("~")))

    def sendCommand(self, command):
        if(self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                if stdout.channel.recv_ready():
                    alldata = stdout.channel.recv(1024)
                    prevdata = b"1"
                    while prevdata:
                        prevdata = stdout.channel.recv(1024)
                        alldata += prevdata

                    print(str(alldata, "utf8"))
        else:
            self.log("### Connection not opened. ###".format(self), fg='red')

    def copyFile(self,path):
        with SCPClient(self.client.get_transport()) as scp:
            scp.put(path,  "/tmp")

    def zipdir(self,path, ziph):
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file))

    def log(self, msg, fg='yellow'):
        sys.stderr.write(bold(msg + '\n', fg=fg))
