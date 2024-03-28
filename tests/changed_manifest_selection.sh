#!/bin/bash

python identify_changed_manifests_for_testing.py \
    --changed_files_path changed-files.txt \
    --current_templates_url https://raw.githubusercontent.com/adknowledgeportal/data-models/main/modules/template/templates.csv \
    --new_templates_path ./modules/template/templates.csv \
    --csv_model_path ./AD.model.csv \
    --template_config_path ./dca-template-config.json \
    --output_file_path changed-templates.json
