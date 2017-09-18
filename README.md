# JOARA

## Code Details

1. **Infrastructure** - Provisiong of Infrastructure ARM templates, configuring jenkins and docker images
2. **Infrastructure/provisioning** - Provisioning Azure resources
3. **Infrastructure/images_version** - Images Version metadata
4. **Infrastructure/images** - Docker images
5. **Infrastructure/configure** - Jenkins Configuration
6. **joara-app-provision** - Joara CLI


## Pre-Setup Machine

### Usage in Windows

1. Install miniconda Python3.6 https://conda.io/miniconda.html

This will create a Command line window called "Anaconda" prompt

```shell
2. cmd> conda  create -n vjoaraapp3 python
3. cmd> activate vjoaraapp3
```

### Usage in Linux


```shell
> wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
> chmod +x Miniconda3-latest-Linux-x86_64.sh
> ./Miniconda3-latest-Linux-x86_64.sh
> export PATH=/home/$USER/miniconda3/bin:$PATH
> conda create -n vjoaraapp3 python
> source activate vjoaraapp3
```

### Pre-Setup JOARA

```shell
> git clone https://github.com/Snap-Analytx/joara-main.git
> cd joara-main
> pip install --editable joara-app-provision
```

**_Azure credentials and others details can be configured in _cluster.ini_ file_**

## JOARA COMMANDS

### Bootstrap datacenter

**all** - Creates ACS, ACR and Stroage

### To Bootstrap DEV datacenter

```shell
> joara -d dev bootstrap --group all --verbose
```

### To Bootstrap TEST datacenter

```shell
> joara -d test bootstrap --group all –-verbose
```

### To Bootstrap PROD datacenter

```shell
> joara -d prod bootstrap --group all --verbose
```

### To Bootstrap JENKINS datacenter

```shell
> joara -d jenkins bootstrap --group jenkins --verbose
```

### Configuring Jenkins

Get Jenkins Credentials and use it in the UI
```shell
> joara -d jenkins jenkinsconfigure --group pre-jenkins --verbose
```

Configure Jenkins 

```shell
> joara -d jenkins jenkinsconfigure --group jenkins --verbose
```

### Configuring GitHub

1. Creates repo with anodejs
2. Creates 3 branches dev,test and master
3. Creates Hook for the repo

```shell
> joara gitconfigure --group git --image anodejs --task all --verbose
```

### Docker Image Opereations - (only from Linux with docker)


Datacenter = dev/test/prod

#### To Build Docker


```shell
> joara -d {datacenter} image --images nodejso --task build --verbose
```

#### To Push Docker

```shell
> joara -d {datacenter} image --images nodejso --task push --verbose
```

#### To Deploy Docker

```shell
> joara -d {datacenter} image --images nodejso --task deploy --count 1 --verbose
```


### Get ACS Details

To Get IP of the service where it is running, Datacenter = dev/test/prod

```shell
> joara -d {datacenter} image --images nodejso --task getservice --verbose
```


## To Destroy existing resources

```shell
joara -d prod destroy --group all --verbose
joara -d dev destroy --group all --verbose
joara -d test destroy --group all --verbose
joara -d jenkins destroy --group all --verbose
```
