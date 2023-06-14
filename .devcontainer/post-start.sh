#!/bin/bash

# create .synapseConfig file with PAT stored in repository secrets
echo -e "[authentication]\nauthtoken = $SYNAPSE_PAT" > .synapseConfig

# create Google api service account creds file for schematic
echo $SCHEMATIC_SERVICE_ACCOUNT_CREDS > schematic_service_account_creds.json
