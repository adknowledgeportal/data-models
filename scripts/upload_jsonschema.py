import os
import glob
from pathlib import Path
from json import load
from importlib_metadata import files

import synapseclient
from synapseclient.core.exceptions import SynapseHTTPError
from synapseclient.services.json_schema import JsonSchemaService, JsonSchemaOrganization

# Environment Variables are set in the github workflow
ORG_NAME = os.environ.get("SYNAPSE_ORGANIZATION")
VERSION = os.environ.get("RELEASE_TAG")


def import_json_schema(filename: str) -> dict:
    """
    Load the schema as a dictionary from the generated files.
    """
    with open(filename, "r") as f:
        schema = load(f)

    return schema

def get_org(js: JsonSchemaService) -> JsonSchemaOrganization:
    """
    Create or get the JsonSchemaOrganization for the given organization name.
    """
    try:
        json_schema_org = js.create_organization(ORG_NAME)
    except SynapseHTTPError as e:
        if e.response.status_code == 400 and "already exists" in e.response.text:
            json_schema_org = js.JsonSchemaOrganization(ORG_NAME)
        else:
            raise e

    return json_schema_org


# Log in to synapse
syn = synapseclient.Synapse()
syn.login()
syn.get_available_services()

print(VERSION, ORG_NAME)

# Get the relevant org from synapse
js = syn.service("json_schema")
json_schema_org = get_org(js)

# Iterate through directory with jsonschema files and register each one
files = glob.glob("*.json")
for i, file in enumerate(files):
    schema = import_json_schema(file)
    schema_name = Path(file).stem
    schema_name = "ad." + schema_name.replace("_", ".").replace("-", ".").replace("validation.","")
    print(f"Uploading schema {i+1}/{len(files)}: {schema_name}")

    try:
        json_schema_org.create_json_schema(schema, schema_name, VERSION.replace("v", ""))
    except SynapseHTTPError as e:
        version_already_exists_message = f"Semantic version: '{VERSION.replace('v', '')}' already exists for this JSON schema"
        if e.response.status_code == 400 and version_already_exists_message in e.response.text:
            print(f"Version {VERSION} already exists for schema {schema_name}, skipping...")
        else:
            raise e
