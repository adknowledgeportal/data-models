# AD Knowledge Portal data models

- **AD.model.\* ([csv](https://github.com/adknowledgeportal/data-models/blob/main/AD.model.csv) | [jsonld](https://github.com/adknowledgeportal/data-models/blob/main/AD.model.jsonld))**: this is the current, "live" version of the AD Portal data model. It is being used by both the staging and production versions of the multitenant Data Curator App. It was initially produced from the legacy.AD.model, with additional changes to make it work better with DCA.
  
- **legacy.AD.model.\<_date_\>.\* ([csv](https://github.com/adknowledgeportal/data-models/blob/main/legacy.AD.model.2023.08.csv) | [jsonld](https://github.com/adknowledgeportal/data-models/blob/main/legacy.AD.model.2023.08.jsonld))**: this is constructed by running the `get_legacy_data_model.py` script. This legacy data model will always represent _just_ the metadata templates from the AD Portal Synapse project, plus the valid values from the latest version of the dictionary schemas in the synapseAnnotations repo.
  
- **divco.data.model.v1.\* ([csv](https://github.com/adknowledgeportal/data-models/blob/main/divco.data.model.v1.csv) | [jsonld](https://github.com/adknowledgeportal/data-models/blob/main/divco.data.model.v1.jsonld))**: this is a pilot data model that was constructed for the Diverse Cohorts project. It is no longer being used by DCA.

## Editing data models
If you want to make changes to the live data model, create a new branch, make changes, and open a pull request. The main branch of this repo is protected to avoid conflicts. 

## Automation
There is a Github Action (`ci.yml`) that installs `schematic` and runs `schema convert` on the csv version of the live data model any time a pull request is opened that includes changes to that csv. This generates a new version of the jsonld from that csv and commits it to the PR branch. 

## Developing in a codespace
If you want to make changes to the data model and test them out by generating manifests with `schematic`, you can use the devcontainer in this repo with a Github Codespace. This will open a container in a remote instance of VSCode and install the latest version of schematic.

Codespace secrets: 
- SYNAPSE_PAT: scoped to view and download permissions on the sysbio-dcc-tasks-01 Synapse service account
- SERVICE_ACCOUNT_CREDS: these are creds for using the Google sheets api with schematic

:warning: If you are working in a Github Codespace, do NOT commit any Synapse credentials to the repository and do NOT use any real human data when testing data model function. This is not a secure environment!
