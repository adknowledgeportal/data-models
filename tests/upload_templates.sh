#!/bin/bash
# upload metadata templates to synapse
# if running locally set SYNAPSE_TOKEN_DPE in your environment

SYNAPSE_UPLOAD_FOLDER_ID=syn64416308


if [ -n "${SYNAPSE_TOKEN}" ]; then
  echo "Using synapse token from env var"
  synapse login -p "${SYNAPSE_TOKEN}"
else
  echo No credentials found
fi

echo Uploading manifests to "$SYNAPSE_UPLOAD_FOLDER_ID"

shopt -s extglob

MANIFESTS=("$PWD"/*.@(xlsx|xls))

for MANIFEST in ${MANIFESTS[@]};
do
  synapse store --parentId "$SYNAPSE_UPLOAD_FOLDER_ID" --noForceVersion "$MANIFEST"
done

echo "✓ Done!"