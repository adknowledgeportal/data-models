#!/bin/bash
# generate GoogleSheets templates
# if using locally run with ./generate_all_manifests.sh from tests directory

TEST_CONFIG_PATH=../dca-template-config.json
TEST_CONFIG=dca-template-config.json
SCHEMATIC_CONFIG_PATH=../schematic-config.yml
SCHEMATIC_CONFIG=schematic-config.yml
#CHANGED_TEMPLATE_CONFIG=changed-templates.json
CREDS_PATH=../schematic_service_account_creds.json
CREDS=sheets_creds.json
DATA_MODEL_PATH=../AD.model.jsonld
DATA_MODEL=AD.model.jsonld
EXCEL_DIR=../current-excel-manifests
JSON_DIR=../current-manifest-schemas
SLEEP_THROTTLE=30 # API rate-limiting, need to better figure out dynamically based on # of templates

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

# Set up templates config
cp $TEST_CONFIG_PATH $TEST_CONFIG
echo "✓ Using copy of $TEST_CONFIG_PATH for test"

TEMPLATES=($(jq '.manifest_schemas[] | .schema_name' $TEST_CONFIG | tr -d '"'))
#TITLES=($(jq '.manifest_schemas[] | .display_name' $TEST_CONFIG | tr -d '"'))
echo "✓ Using config with ${#TEMPLATES[@]} templates..."

# CHANGED_TEMPLATES=($(jq '.[] | .schema_name' $CHANGED_TEMPLATE_CONFIG | tr -d '"'))
# echo "✓ Using ${#CHANGED_TEMPLATES[@]} templates from $CHANGED_TEMPLATE_CONFIG..."

# Setup data model
cp $DATA_MODEL_PATH $DATA_MODEL
echo "✓ Set up $DATA_MODEL for test"

# Setup logs
mkdir -p $LOG_DIR

for i in ${!TEMPLATES[@]}
do
  echo ">>>>>>> Generating ${TEMPLATES[$i]}"
  schematic manifest --config schematic-config-test.yml get -dt "${TEMPLATES[$i]}" --title "${TEMPLATES[$i]}" -oxlsx "$EXCEL_DIR/${TEMPLATES[$i]}.xlsx" | tee $LOG_DIR/${TEMPLATES[$i]%.*}_log
  sleep $SLEEP_THROTTLE
done

echo "Moving manifest json schemas to $JSON_DIR"
mv *.schema.json $JSON_DIR

echo "Cleaning up test directory"
rm -f $CREDS $TEST_CONFIG $DATA_MODEL *.manifest.csv

echo "✓ Done!"