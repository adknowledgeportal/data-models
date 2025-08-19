import os
import glob
from pathlib import Path
from json import load
from importlib_metadata import files

import synapseclient

ORG_NAME = os.environ.get("SYNAPSE_ORGANIZATION")
VERSION = os.environ.get("RELEASE_TAG")


def import_json_schema(filename: str) -> tuple[dict, str]:
    with open(filename, "r") as f:
        schema = load(f)

    uri = format_uri(filename)

    return schema, uri

def format_uri(filename: str) -> str:
    uri = f"{Path(filename).stem}"
    return uri

def create_org(syn, js,) -> None:
    all_orgs = js.list_organizations()
    for org in all_orgs:
        if org["name"] == ORG_NAME:
            syn.logger.info(f"Organization {ORG_NAME} already exists.")
            break
    else:
        syn.logger.info(f"Creating organization {ORG_NAME}.")
        js.create_organization(ORG_NAME)



def register_schema(schema: dict, uri: str,) -> None:
    syn = synapseclient.Synapse()
    syn.login()

    js = syn.service("json_schema")
    create_org(syn, js)

    json_schema_org = js.JsonSchemaOrganization(name=ORG_NAME)

    json_schema_org.get()

    json_schema_org.create_json_schema(schema, uri, VERSION)

    
files = glob.glob("*.json")
for file in files:
    schema, uri = import_json_schema(file)
    register_schema(schema, uri)