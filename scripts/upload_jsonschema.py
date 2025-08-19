import os
import glob
from pathlib import Path
from json import load
from importlib_metadata import files

import synapseclient

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

def create_org(syn, js,) -> None:
    """
    Check if the given organization exists on synapse, and create it if it doesn't.
    """
    all_orgs = js.list_organizations()
    for org in all_orgs:
        if org["name"] == ORG_NAME:
            syn.logger.info(f"Organization {ORG_NAME} already exists.")
            break
    else:
        syn.logger.info(f"Creating organization {ORG_NAME}.")
        js.create_organization(ORG_NAME)

def register_schema(schema: dict, filename: str,) -> None:
    """
    Register the given JsonSchema on synapse under the organization provided
    """
    syn = synapseclient.Synapse()
    syn.login()

    js = syn.service("json_schema")
    create_org(syn, js)

    json_schema_org = js.JsonSchemaOrganization(name=ORG_NAME)

    json_schema_org.get()

    uri = Path(filename).stem
    json_schema_org.create_json_schema(schema, uri, VERSION)

# Iterate through directory with jsonschema files and register each one
files = glob.glob("*.json")

for file in files:
    schema = import_json_schema(file)
    register_schema(schema, file)