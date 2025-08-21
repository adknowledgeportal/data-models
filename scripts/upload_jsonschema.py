import os
import glob
from pathlib import Path
from json import load
from importlib_metadata import files

import synapseclient
from synapseclient.core.exceptions import SynapseHTTPError

# Environment Variables are set in the github workflow
ORG_NAME = os.environ.get("SYNAPSE_ORGANIZATION")
VERSION = os.environ.get("RELEASE_TAG")


def import_json_schema(filename: str) -> dict:
    """
    Load the schema as a dictionary from the generated files. Build 
    """
    with open(filename, "r") as f:
        schema = load(f)

    return schema

def get_org(js,) -> None:
    """
    Create or get the JsonSchemaOrganization for the given organization name.
    """
    try:
        json_schema_org = js.create_organization(ORG_NAME)
    except SynapseHTTPError as e:
        if e.response.status_code == 400 and "already exists" in e.response.text:
            print(f"Organization {ORG_NAME} already exists.")
            json_schema_org = js.get_organization(ORG_NAME)
        else:
            raise e

    return json_schema_org

def register_schema(schema: dict, filename: str, json_schema_org) -> None:
    """
    Register the given JsonSchema on synapse under the organization provided.
    """

    uri = Path(filename).stem
    json_schema_org.create_json_schema(schema, uri, VERSION)



# Log in to synapse
syn = synapseclient.Synapse()
syn.login()

# Get the relevant org from synapse
js = syn.service("json_schema")
json_schema_org = get_org(js)

# Iterate through directory with jsonschema files and register each one
files = glob.glob("*.json")
for file in files:
    schema = import_json_schema(file)
    register_schema(schema=schema, file=file, json_schema_org=json_schema_org)
