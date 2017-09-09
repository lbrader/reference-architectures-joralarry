#!/bin/bash


#set -ex

Color_Off='\033[0m'       # Text Reset
Red='\033[0;31m'          # Red
Green='\033[0;32m'        # Green
BRed='\033[1;31m'         # Red
BGreen='\033[1;32m'       # Green

run_command () {
   success_echo "${1}"
   eval $1
   if [ $? -ne 0 ]; then
    failure_echo "${TO_DATACENTER} was not successful"
    exit 1
   fi
}

success_echo () {

   echo -e "${BGreen}${1}${Color_Off}"
}

failure_echo () {

   echo -e "${BRed}${1}${Color_Off}"
}

TO_DATACENTER="$1"
IMAGE_NAME="$2"

if [ -z "$TO_DATACENTER" ] ; then
    success_echo "\$TO_DATACENTER was not set"
    exit 1
fi

pre_setup_env ()
{
    success_echo "Installing JOARA"
    export PATH=/opt/conda/bin:$PATH
    source activate vjoaraapp3
    CMD="pip install --editable joara-app-provision"
    run_command "${CMD}"

}

image_default_action ()
{
    image_action="build,push,deploy"
    success_echo "Docker Image build,push, deploy"
    export PATH=/opt/conda/bin:$PATH
    source activate vjoaraapp3
    IFS=', ' read -r -a array <<< "$image_action"
    for action in "${array[@]}"
    do
        CMD="joara -d $TO_DATACENTER image --images $IMAGE_NAME --task ${action}"
        run_command "${CMD}"
    done

}

pre_setup_env
image_default_action



rm -rf logs