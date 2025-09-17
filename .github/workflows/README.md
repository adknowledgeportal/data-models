# CI/CD Documentation
## Build Workflow

### Purpose
The `build` workflow is used to test and surface changes made to the data model as updated metadata templates in synapse.

### Triggers
The `build` workflow runs whenever all of the following conditions are met:
* a PR is open and targets the `main` branch
* the PR indludes modifications to the files in the `modules` subdirectory
* the PR is modified by either committing changes to the branch while the PR is open or by closing the PR

### Necessary Actions from Contributors
The `build` workflow is designed to integrate seamlessly into the regular data model maintenance flow. When a PR targeting `main` is open and changes are committed, the changes will be tested through the creation of a google sheet of the appropriate manifest. A comment will be added to the PR discussion with a link to the sheet for inspection.
When the pull request is merged, new excel files will be created for the modified data types and committed to `main`. These excel files will also be uploaded to the specified folder on Synapse.

### Outputs
While a PR is open and under development
* Test templates are created and linked in the PR comments

When a PR is merged
* Modified excel templates are committed to `main`
* All JSONSchema files are generated and committed to `main`
* Modified excel templates are uploaded to synapse


### Diagrams

<details>

<summary>Mermaid diagram for build workflow</summary>

```mermaid
%%{init: {"flowchart": {"defaultRenderer": "elk"}, "theme": "base", "themeVariables": {"fontSize": "12px", "lineColor": "#ffffff", "edgeLabelBackground": "#ffffff", "edgeStrokeWidth": "2px", "primaryBorderColor": "#000000"}}}%%
    flowchart TD
        A[Create/Update PR] --> B{PR Action Type}
        B -->|opened/synchronize| C[PR trigger - paths: modules/**]
        B -->|labeled| D[PR labeled trigger]
        
        C --> E{Triggering actor<br>!=<br>commit-to-main-bot?}
        D --> E
        E -->|Yes| F[schema-convert job]
        E -->|No| Z1[Skip workflow]
        
        F --> F1[Create GitHub App Token]
        F1 --> F2[Checkout PR branch with token]
        F2 --> F3[Setup Python 3.10]
        F3 --> F4[Install libraries<br>from requirements.txt]
        F4 --> F5[List changed files<br>for manifest testing]
        F5 --> F6[Assemble CSV data model]
        F6 --> F7[Commit CSV changes]
        F7 --> F8[Convert CSV to JSON-LD]
        F8 --> F9[Commit JSON-LD changes]
        F9 --> F10[Identify changed manifests]
        F10 --> F11[Save changed manifests to output]
        F11 --> F12[Delay 60 seconds]
        
        F12 --> G{Action != labeled?}
        F12 --> H{Has automerge label?}
        
        G ---->|Yes| I[test job]
        H -->|Yes| H2{GitHub event != opened<br>and<br>GitHub event != synchronize?}
        
        H2 -->|Yes| J[merge job]
        H2 -->|No| Z2[Skip workflow]
        
        I --> I1[Print changed manifests]
        I1 --> I2[Create GitHub App Token]
        I2 --> I3[Checkout PR branch]
        I3 --> I4[Setup Python 3.10]
        I4 --> I5[Install libraries]
        I5 --> I6[Generate test manifests]
        I6 --> I7[Create Test Suite Report with Docker/R]
        I7 --> I8[Report test suite as PR comment]
        I8 --> I9[Upload test artifacts]
        
        J --> J1[Create GitHub App Token]
        J1 --> J2[Auto-merge PR with squash]
        J2 --> J3[Delete development branch]
        
        J3 --> K[generate-and-upload-manifests job]
        
        K --> K1[Print changed manifests]
        K1 --> K2[Create GitHub App Token]
        K2 --> K3[Checkout main branch]
        K3 --> K4[Setup Python 3.10]
        K4 --> K5[Install libraries]
        K5 --> K6[Generate changed manifests]
        K6 --> K7[Commit manifests to main]
        K7 --> K8[Generate JSONSchema]
        K8 --> K9[Commit schemas to main]
        K9 --> K10[Upload manifests to Synapse]
        
    subgraph Legend
        direction TB
        triggers[Triggers]
        jobs[Jobs]
        outputs[Outputs]
        triggers ~~~ jobs ~~~ outputs
        style triggers fill:#ffeb3b,stroke-width:0px
        style jobs fill:#e3f2fd,stroke-width:0px
        style outputs fill:#4caf50,stroke-width:0px
    end
    
    style A fill:#ffeb3b
    style C fill:#ffeb3b
    style D fill:#ffeb3b
    style F fill:#e3f2fd
    style I fill:#e3f2fd
    style J fill:#e3f2fd
    style K fill:#e3f2fd
    style F7 fill:#4caf50
    style F9 fill:#4caf50
    style I8 fill:#4caf50
    style I9 fill:#4caf50
    style J2 fill:#4caf50
    style K7 fill:#4caf50
    style K9 fill:#4caf50
    style K10 fill:#4caf50
```
</details>


## Release Workflow

### Purpose
The `release` workflow is used to mint JSONSchema files for the data model as part of a release and register them on Synapse so that they may be bound to entities later.

### Triggers
The `release` workflow runs whenever a relase of the data model is minted, that is, when a new version tag is pushed to the repository.

### Necessary Actions from Contributors
Publish a new Release on github and specify a new tag.

### Outputs
* All JSONSchema files are registered with the specified organization on Synapse under the new version tag


### Diagrams

<details>

<summary>Mermaid diagram for release workflow</summary>

```mermaid
%%{init: {"flowchart": {"defaultRenderer": "elk"}, "theme": "base", "themeVariables": {"fontSize": "12px", "lineColor": "#ffffff", "edgeLabelBackground": "#ffffff", "edgeStrokeWidth": "2px", "primaryBorderColor": "#000000"}}}%%
    flowchart TD
    A[Create Git Tag] --> B[Push tag trigger]
    
    B --> C{Triggering actor<br>!=<br>commit-to-main-bot?}
    C -->|Yes| D[release job]
    C -->|No| Z[Skip workflow]
    
    D --> D1[Create GitHub App Token]
    D1 --> D2[Checkout main branch]
    D2 --> D3[Setup Python 3.10]
    D3 --> D4[Install libraries<br>from requirements.txt]
    D4 --> D5[Register JSONSchema to Synapse]
    subgraph Legend
        direction TB
        triggers[Triggers]
        jobs[Jobs]
        outputs[Outputs]
        triggers ~~~ jobs ~~~ outputs
        style triggers fill:#ffeb3b,stroke-width:0px
        style jobs fill:#e3f2fd,stroke-width:0px
        style outputs fill:#4caf50,stroke-width:0px
    end
    
    style A fill:#ffeb3b
    style B fill:#ffeb3b
    style D fill:#e3f2fd
    style D5 fill:#4caf50
```
</details>