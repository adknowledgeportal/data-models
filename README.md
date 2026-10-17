# The AD Knowledge Portal data model

- [Production data model](#production-data-model)
- [Editing data models](#editing-data-models)
  * [Github branch procedure:](#github-branch-procedure)
  * [Editing attributes by module:](#editing-attributes-by-module)
    + [Adding a new valid value to an existing manifest column:](#adding-a-new-valid-value-to-an-existing-manifest-column)
    + [Adding a new column to a manifest template:](#adding-a-new-column-to-a-manifest-template)
  * [Notes on collaboratively editing csvs](#notes-on-collaboratively-editing-csvs)
- [Release Process](#release-process)
- [Developing in a codespace](#developing-in-a-codespace)
- [Legacy data models:](#legacy-data-models)            

## Production data model
[AD.model.csv](https://github.com/adknowledgeportal/data-models/blob/main/AD.model.csv)


## Editing data models

:warning: Do **not** edit `AD.model.csv` by hand! :warning:

### Github branch procedure:

The main branch of this repo is protected, so you cannot push changes to main. To make changes to the data model:
1. Create a new branch in this repo and give it a descriptive name (the name will later be used to generate release notes). The CI/CD workflows will not work from a private fork.
2. On that branch, make and commit any changes. You can do this by cloning the repo locally or by [using a Github codespace](#developing-in-a-codespace). Please write informative commit messages in case we need to track down data model inconsistencies or introduced bugs.
3. Open a pull request and request review from someone else on the AD DCC team. The `register-schema` job will run as soon as you open the PR. If this action fails, something about the data model csv could not generate and/or register JSON schemas.
4. Once all the necessary changes have been made, the `register-schema` job completes successfully, and the PR is approved, the PR is ready for merge.

For more information on the automated workflows, review the CI/CD documentation for the [build workflow](.github/workflows/README.md#register-schema-workflow).

> **Note on unversioned schema registration:** When a PR is open, the `register-schema` workflow registers schemas to the `test.ad` Synapse organization without a semantic version. This is safe to do across multiple concurrent PRs — Synapse assigns each registration a unique internal `version_id`, so schemas from different PRs are stored independently and do not overwrite one another.

### Editing attributes by module:

> [!NOTE]
> For more information what is supported wthin the CSV data model, please proceed to this [documentation](https://python-docs.synapse.org/en/stable/explanations/curator_data_model/). Here are some examples, adding validation rules: https://github.com/adknowledgeportal/data-models/pull/252, context refactor: https://github.com/adknowledgeportal/data-models/pull/253, and adding conditional logic https://github.com/adknowledgeportal/data-models/pull/259.

The full `AD.model.csv` file has over 1400 attributes and is unwieldy to edit and hard to review changes for. For ease of editing, the full data model is divided into "module" subfolders, like so:

```
data-models/
├── AD.model.csv (do not edit!)
└── modules/
    ├── biospecimen/
    │   ├── specimenID.csv
    │   ├── organ.csv
    │   └── tissue.csv
    └── sequencing/
        ├── readLength.csv
        └── platform.csv
```
Within each module, every attribute in the data model where `Parent` = `ManifestColumn` has its own csv, named after that attribute (example: `organ.csv`). Any valid values of the attribute "organ" have `Parent` = `organ` and are listed as rows in the file `organ.csv`. Attributes with `Parent` = `ManifestColumn` are used as columns in metadata and annotation manifest templates. Attributes with `Parent` = `ManifestTemplate` describe the templates themselves. At this time, any other value for `Parent` means the attribute is a valid value of some other enumerated attribute. 

Some common data model editing scenarios are:

#### Adding a new valid value to an existing manifest column: 
1. If you wanted to add a new valid value "eyeball" to our existing column attribute "organ", after making a new branch and opening the repo either locally or within a codespace, you would go to `modules/biospecimen/organ.csv`.
1. Then, create a new row for an attribute named "eyeball", with a description and source (preferably an ontology URI). In the `Parent` column, make sure the value is "organ".
1. Next, find the row for the attribute "organ" (should be the first row), and w/in the valid values column, add "eyeball" to the comma-separated list of valid values.
1. Save your changes and write an informative commit. Please try to add valid values alphabetically!
   
#### Adding a new column to a manifest template: 
1. If you wanted to add the column "furColor" to the "model-ad_individual_animal_metadata" template, first decide which module the new column should belong to. In this case, "MODEL-AD" makes the most sense.
1. W/in the `MODEL-AD` subfolder, create a new csv called `furColor.csv` with the required schematic column headers. Describe the attribute "furColor" as necessary and make sure `Parent` = `ManifestColumn`. Add any valid values for "furColor" as new rows to this csv as described in the previous scenario.
1. Find the manifest template attributes in `modules/template/templates.csv`. In the "model-ad_individual_animal_metadata" row, add your new column "furColor" to the comma-separated list of attributes in the `DependsOn` column.
1. Save your changes and write an informative commit.

#### Adding a new template to the data model:
1. If you wanted to add a new template to the data model, first add the template to the bottom of the 'template.csv' file, with the column names in the order they will appear.
      Example: 'assay_spatialTranscriptomics_metadata_template,SysBio spatial transcriptomics metadata template schema,,"Component, individualID, biospecimenID, fileFormat, sequenceAnalysis, runID, captureArea, readIndicator, spatialRead1, spatialRead2",,False,ManifestTemplate,,sysbio.metadataTemplates-assay.spatialTranscriptomics,,,template'
1. Stage, commit, and open a PR with these two changes, requesting review by another AD data manager. Once approved and merged, a GitHub Action workflow will run that generates and registers jsonschemas along with creation of recordsets for Curator. You will know when they are complete with a green check.

For more advanced data modeling scenarios like adding conditional logic, creating validation rules, or creating new manifests, please consult the #ad-dcc-team slack channel.

### Notes on collaboratively editing csvs

A persistent issue is that manually editing csvs is challening. Some columns in our modules are very short, and others are veeeeery long (Description, Valid Values). Some options for working on csvs, and their pros and cons:

- Editing in the Github UI :octocat: : convenient, but challenging to keep track of columns in plain text format. 
- Cloning the repo, making a branch, and opening csvs locally in Excel or another spreadsheet program 🖥️ : probably the best UI experience, but involves a few extra steps with git.
- Using a [Github codespace](#developing-in-a-codespace) to launch VSCode in the browser, and editing with the pre-installed RainbowCSV extension 🌈 : Still difficult to edit csvs as plain text, but the color formatting and ability to use a soft word wrap makes it much easier to distinguish columns. [RainbowCSV](https://marketplace.visualstudio.com/items?itemName=mechatroner.rainbow-csv) lets you designate "sticky" rows and columns for easier scrolling, and also has a nice "CSVLint" function that will check for formatting errors after you make changes.

We are exploring better solutions to this problem -- if you have ideas, tell us!

## Release Process

> **Note:** A release has five steps. Steps 1 and 2 are the GitHub release itself: schemas are first registered to a test Synapse organization, then promoted to production. Publishing a pre-release registers schemas to `test.ad`; promoting it to a full release registers to `sage.schemas.ad`. Registering to production automatically rebuilds the Excel templates; Step 3 checks that it worked. Step 4 updates Core Models, which needs a PR to be approved and merged by hand, and Step 5 announces the update in Slack.
>
> **Tag format:** Release tags must follow `vX.Y.Z` (e.g. `v1.2.0`). Tags with pre-release suffixes like `-rc1`, `-beta`, or `-alpha` will cause schema registration to fail.

#### Step 1 — Publish a Pre-release (registers to `test.ad`)
1. From the main repository page, click on the `Releases` tab on the right.
2. Select `Draft a new release` at the top right of the page.
3. Click `Tag: Select Tag` and create a new tag following the convention `v<major>.<minor>.<patch>`. Ensure the version has not been previously used.
4. Ensure `Target` is set to `main`.
5. Under `Release Title`, enter the version number. Under `Release Notes`, click `Generate release notes` and review for accuracy.
6. Check **"Set as a pre-release"**.
7. Click `Publish release`. This triggers schema registration to the `test.ad` Synapse organization. Review the workflow summary or PR comment to verify schemas were registered correctly.

#### Step 2 — Promote to Full Release (registers to `sage.schemas.ad`)
1. Once schemas in `test.ad` are validated, return to the pre-release on GitHub.
2. Edit the release and uncheck **"Set as a pre-release"** (or click **"Promote to full release"**).
3. Click `Update release`. This triggers schema registration to the `sage.schemas.ad` production Synapse organization.

#### Step 3 — Check the Excel templates on the AD Dictionary site
Registering the schemas to `sage.schemas.ad` automatically starts the **Build Excel templates** workflow, which rebuilds the Excel templates and uploads them to the [AD Metadata Dictionary folder](https://www.synapse.org/Synapse:syn25878249). It takes about 5 minutes after registration finishes.
1. In the **Actions** tab, check that the **Build Excel templates** run for the release completed successfully.
2. On the [AD Metadata Dictionary folder](https://www.synapse.org/Synapse:syn25878249), open a few templates and check that the newest file version has:
    - version comment `sage.schemas.ad <version>` (e.g. `sage.schemas.ad 2.0.0`)
    - annotation `modelVersion` matching the release version
    - annotation `releaseDate` matching the release date. This is the date the schemas were registered, in UTC, so a release published after about 5 pm Pacific shows the next day's date.

If the run didn't start or failed, it can be run manually from the **Actions** tab. See the CI/CD documentation for the [build-excel-templates workflow](.github/workflows/README.md#build-excel-templates-workflow).

#### Step 4 — Update Core Models
1. **Start the update right after the JSON schemas are generated** (or wait for the automatic run at 06:00 UTC, which is 11 pm Pacific)
    - Go to [Sage-Bionetworks/core-models](https://github.com/Sage-Bionetworks/core-models) → **Actions** tab.
    - In the left sidebar, click **Update Schema Data → Deploy Pages → Publish to CoreModels**.
    - Click **Run workflow**. Leave **org_name blank**: filling it in may drop other organizations' schemas. Keep the branch on `main`, then click the green **Run workflow** button.
    - After a few minutes it opens a pull request from `github-actions[bot]`, with a branch named like `automated/schema-update-<number>`.
    - Set yourself as the reviewer.
2. **Approve the PR**
    - Open the **Pull requests** tab and click the new bot PR. If several are open, use the newest; merging it is enough.
    - Optionally, check under **Files changed** that `public/data.json` includes AD at the new release version.
    - Click **Review changes** (top right of Files changed), choose **Approve**, then **Submit review**.
3. **Merge it**
    - Back on the **Conversation** tab, click the green merge button at the bottom and confirm.
    - Merging deploys the GitHub Pages site and publishes to the CoreModels app, which takes about 15 minutes.
    - Check CoreModels to verify changes.

#### Step 5 — Announce the update
Post in the Slack channels **#adtr-data-model-updates** and **#adtr-data-managers** that the data model has been updated, with a link to the release (e.g. `https://github.com/adknowledgeportal/data-models/releases/tag/v2.0.0`).

For more information on the automated workflows, see the CI/CD documentation for the [register-schema workflow](.github/workflows/README.md#register-schema-workflow) and the [build-excel-templates workflow](.github/workflows/README.md#build-excel-templates-workflow).

## Developing in a codespace

:warning: If you are working in a Github Codespace, do NOT commit any Synapse credentials to the repository and do NOT use any real human data when testing data model function. This is not a secure environment!

If you want to make changes to the data model and test them out by generating manifests with `schematic`, you can use the devcontainer in this repo with a Github Codespace. This will open a container in a remote instance of VSCode and install the latest version of schematic. The devcontainer also installs the Rainbow CSV extension. You can make changes, commit them, and open a PR from the codespace. 

Codespace secrets: 
- SYNAPSE_PAT: scoped to view and download permissions on the sysbio-dcc-tasks-01 Synapse service account
- SERVICE_ACCOUNT_CREDS: these are creds for using the Google sheets api with schematic
- GENERATE_MANIFESTS_ON_ACTION: this fine-grained PAT lets manifests be successfully generated despite branch protection, has read/write access to actions, and has repo access to adknowledgeportal/data-models 

## Legacy data models:
Previous versions of the data model live in the `legacy-data-models/` folder. This include the Diverse Cohorts pilot model and the intial "legacy" model representing the AD Portal Synapse project metadata dictionary and metadata templates from August 2023. These are not being used by DCA.

