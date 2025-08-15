#!/bin/bash
# upload metadata templates to synapse
# if running locally set SYNAPSE_AUTH_TOKEN in your environment

set -exo pipefail
shopt -s extglob

CHANGED_TEMPLATES=$1

echo Uploading manifests to "${SYNAPSE_UPLOAD_FOLDER_ID}"

for MANIFEST in ${CHANGED_TEMPLATES[@]};
do
  echo "Uploading $MANIFEST"
  synapse store --parentId "${SYNAPSE_UPLOAD_FOLDER_ID}" --noForceVersion "$MANIFEST"
done

echo "✓ Done!"