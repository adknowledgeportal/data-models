# AD Knowledge Portal data models

- **AD.model.\* ([csv](https://github.com/adknowledgeportal/data-models/blob/main/AD.model.csv) | [jsonld](https://github.com/adknowledgeportal/data-models/blob/main/AD.model.jsonld))**: this is the current, "live" version of the AD Portal data model. It is being used by both the staging and production versions of the multitenant Data Curator App. It was initially produced from the legacy.AD.model, with additional changes to make it work better with DCA.
  
- **legacy.AD.model.\<_date_\>.\* ([csv](https://github.com/adknowledgeportal/data-models/blob/main/legacy.AD.model.2023.08.csv) | [jsonld](https://github.com/adknowledgeportal/data-models/blob/main/legacy.AD.model.2023.08.jsonld))**: this is constructed by running the `get_legacy_data_model.py` script. This legacy data model will always represent _just_ the metadata templates from the AD Portal Synapse project, plus the valid values from the latest version of the dictionary schemas in the synapseAnnotations repo.
  
- **divco.data.model.v1.\* ([csv](https://github.com/adknowledgeportal/data-models/blob/main/divco.data.model.v1.csv) | [jsonld](https://github.com/adknowledgeportal/data-models/blob/main/divco.data.model.v1.jsonld))**: this is a pilot data model that was constructed for the Diverse Cohorts project. It is no longer being used by DCA.

## Editing data models
The main branch of this repo is protected, so you cannot push changes to main. To make changes to the data model:
1. Create a new branch in this repo and give it an informative name. The schema-convert workflow will not work from a private fork.
2. On that branch, make and commit any changes. You can do this by cloning the repo locally or by using a Github codespace ([more info](#developing-in-a-codespace)). Please write informative commit messages in case we need to track down data model inconsistencies or introduced bugs.
3. Open a pull request and request review from someone else on the AD DCC team. The Github Action described [below](#automation) will run as soon as you open the PR. If this action fails, something about the data model csv could not be converted to a json-ld and should be investigated. If this action passes, the PR can be merged with one approving review.
4. After the PR is merged, delete your branch. 

## Automation
There is a Github Action (`schema-convert-ci.yml`) that installs `schematic` and runs `schema convert` on the csv version of the live data model any time a pull request is opened that includes changes to that csv. This generates a new version of the jsonld from that csv and commits it to the PR branch. 

## Developing in a codespace

:warning: If you are working in a Github Codespace, do NOT commit any Synapse credentials to the repository and do NOT use any real human data when testing data model function. This is not a secure environment!

If you want to make changes to the data model and test them out by generating manifests with `schematic`, you can use the devcontainer in this repo with a Github Codespace. This will open a container in a remote instance of VSCode and install the latest version of schematic.

Codespace secrets: 
- SYNAPSE_PAT: scoped to view and download permissions on the sysbio-dcc-tasks-01 Synapse service account
- SERVICE_ACCOUNT_CREDS: these are creds for using the Google sheets api with schematic
