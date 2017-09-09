#!/bin/bash


imagename="$1"
export PATH=/opt/conda/bin:$PATH
source activate vjoaraapp3
pip install --editable joara-app-provision

joara -d dev image --images $imagename --task build
