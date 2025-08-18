#!/bin/bash
# upload metadata templates to synapse
# if running locally set SYNAPSE_AUTH_TOKEN in your environment

set -exo pipefail
shopt -s extglob

IFS=' ' read -r -a CHANGED_TEMPLATES_ARRAY <<< "$1" 

echo Uploading ${#CHANGED_TEMPLATES_ARRAY[@]} manifests to "${SYNAPSE_UPLOAD_FOLDER_ID}"

for template in "${CHANGED_TEMPLATES_ARRAY[@]}";
do
  echo "Uploading $template"
  synapse store --parentId "${SYNAPSE_UPLOAD_FOLDER_ID}" --noForceVersion "$template"
  if  [ $? -eq 0 ]; then
    echo "✓ Manifest $template successfully stored on synapse"
  else
    echo "✗ Manifest $template failed to be stored on synapse"
  fi
done

echo "✓ Done!"