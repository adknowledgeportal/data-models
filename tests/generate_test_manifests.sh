#!/bin/bash
# generate GoogleSheets templates
# if using locally run with ./generate_all_manifests.sh from tests directory

set -e

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
SLEEP_THROTTLE=17 # API rate-limiting, need to better figure out dynamically based on # of templates
CHANGED_TEMPLATES=$1

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

echo "✓ Using ${#CHANGED_TEMPLATES[@]} templates from environment variable."


for i in ${!CHANGED_TEMPLATES[@]}
do
  echo ">>>>>>> Generating ${CHANGED_TEMPLATES[$i]}"
  schematic manifest --config schematic-config-test.yml get -dt "${CHANGED_TEMPLATES[$i]}" --title "${CHANGED_TEMPLATES[$i]}" -s | tee $LOG_DIR/${CHANGED_TEMPLATES[$i]%.*}_log
  sleep $SLEEP_THROTTLE
done

echo "✓ Done!"
