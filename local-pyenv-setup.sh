#!/bin/bash

# use this if you need to set up a new environment locally

# create virtualenv to use develop branch of synapse client
# still using 3.10.9 for schematic compatability (? maybe not important ?)
# pyenv virtualenv 3.10.9 synapse-pyclient-develop
# didn't actually need the develop branch for schema services
# just use a virtualenv for schematic pypi release
pyenv virtualenv 3.10.9 schematic-23.8.1

# activate
#pyenv activate synapse-pyclient-develop
pyenv activate schematic-23.8.1

# install develop branch
# pip install git+https://github.com/Sage-Bionetworks/synapsePythonClient.git@develop

#^ that didn't work

# instead, fork the python client repo and clone it
# activate the virtualenv inside the repo
# then run 
# pip install -e .

# install schematic, which includes synapsclient + pandas
pip install schematic==23.8.1

# install github file fetcher

# actually install node first to get npm
brew install node

# then install the file fetcher
npm install -g github-files-fetcher

# switch back to the adkp/data-models directory
# get the files from the sysbiodccjsonschemas repository
fetcher --url="https://github.com/Sage-Bionetworks/sysbioDCCjsonschemas/tree/master/schema_metadata_templates" --out=.

# delete the PsychEncode subfolder
rm -r schema_metadata_templates/PsychEnchode