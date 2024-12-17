#!/bin/bash
# upload metadata templates to synapse
# if running locally set SYNAPSE_TOKEN_DPE in your environment


SYNAPSE_UPLOAD_FOLDER_ID=syn64416308

echo Uploading manifests to "$SYNAPSE_UPLOAD_FOLDER_ID"

shopt -s extglob

MANIFESTS=("$PWD"/*.@(xlsx|xls))

for MANIFEST in ${MANIFESTS[@]};
do
  synapse store --parentId "$SYNAPSE_UPLOAD_FOLDER_ID" --noForceVersion "$MANIFEST"
done

echo "✓ Done!"