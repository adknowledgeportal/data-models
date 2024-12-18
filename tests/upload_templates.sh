#!/bin/bash
# upload metadata templates to synapse
# if running locally set SYNAPSE_AUTH_TOKEN in your environment

set -e
shopt -s extglob

echo Uploading manifests to "${SYNAPSE_UPLOAD_FOLDER_ID}"

MANIFESTS=("$PWD"/*.@(xlsx|xls))

for MANIFEST in ${MANIFESTS[@]};
do
  echo "Uploading $MANIFEST"
  synapse store --parentId "${SYNAPSE_UPLOAD_FOLDER_ID}" --noForceVersion "$MANIFEST"
done

echo "✓ Done!"