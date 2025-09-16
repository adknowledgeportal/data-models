#!/bin/bash
# generate GoogleSheets templates
# if using locally run with ./generate_all_manifests.sh from tests directory

set -exo pipefail

# TEST_CONFIG_PATH=../dca-template-config.json
# TEST_CONFIG=dca-template-config.json
SCHEMATIC_CONFIG_PATH=../schematic-config.yml
SCHEMATIC_CONFIG=schematic-config.yml
CHANGED_TEMPLATE_CONFIG=changed-templates.json
CREDS_PATH=../schematic_service_account_creds.json
CREDS=sheets_creds.json
DATA_MODEL_PATH=../AD.model.jsonld
DATA_MODEL=AD.model.jsonld
LOG_DIR=logs
SLEEP_THROTTLE=30 # to avoid hitting api rate limits
IFS=' ' read -r -a CHANGED_TEMPLATES_ARRAY <<< "$1" 

# copy schematic-config.yml into tests/ 
cp $SCHEMATIC_CONFIG_PATH $SCHEMATIC_CONFIG
echo "✓ Using schematic configuration settings from $SCHEMATIC_CONFIG"

# Setup for creds
if [ -f "$CREDS_PATH" ]; then
  cp $CREDS_PATH $CREDS
fi

# If testing locally, it might already be in folder; 
# Else, especially if in Actions or Codespace, we need to create it from env var
# See https://github.com/nf-osi/nf-metadata-dictionary/settings/secrets/codespaces
if [ -f "$CREDS" ]; then
  echo "✓ $CREDS -- running tests locally"
elif [ -n "${SCHEMATIC_SERVICE_ACCOUNT_CREDS}" ]; then
  echo "${SCHEMATIC_SERVICE_ACCOUNT_CREDS}" > $CREDS
  echo "✓ Created temp $CREDS for test"
else
  echo "✗ Failed to access stored creds. Aborting test."
  exit 1
fi

# Setup data model
cp $DATA_MODEL_PATH $DATA_MODEL
echo "✓ Set up $DATA_MODEL for test"

# Setup logs
mkdir -p $LOG_DIR

echo "✓ Using ${#CHANGED_TEMPLATES_ARRAY[@]} templates (${CHANGED_TEMPLATES_ARRAY[@]}) from environment variable."

for template in "${CHANGED_TEMPLATES_ARRAY[@]}";
do
  echo ">>>>>>> Generating manifest $template"
  schematic manifest --config schematic-config-test.yml get -dt "$template" --title "$template" -s | tee "$LOG_DIR/${template%.*}_log"
  if  [ $? -eq 0 ]; then
    echo "✓ Manifest $template successfully generated"
  else
    echo "✗ Manifest $template failed to generate"
  fi

  if ${#CHANGED_TEMPLATES_ARRAY[@]} > 1; then
    for i in $(seq 1 $SLEEP_THROTTLE); do
      sleep 1
      printf "\r Waited $i of $SLEEP_THROTTLE seconds"
    done
  fi
done

echo "✓ Done!"
