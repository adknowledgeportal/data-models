#!/usr/bin/env python
""" 
identify_changed_manifests_for_testing.py: Gather templates that have changed

USAGE: 
    python ./scripts/identify_changed_manifests_for_testing.py \
    --changed_files_path ./tests/changed-files.txt \
    --current_templates_url https://raw.githubusercontent.com/adknowledgeportal/data-models/main/modules/template/templates.csv \
    --new_templates_path ./modules/template/templates.csv \
    --csv_model_path ./AD.model.csv \
    --template_config_path ./dca-template-config.json \
    --output_file_path ./tests/changed-templates.json

"""

__author__ = "Abby Vander Linden"
__status__ = "development"

import os
import json
import argparse
import pandas as pd


def get_templates_with_changed_attributes(
    csv_model_path: str, changed_attributes: list
) -> list:
    """List of templates with changes in the data model

    Args:
        csv_model_path (str): relative path to csv data model
        changed_attributes (list): _description_

    Returns:
        list: name of templates with changes
    """
    csv_model = pd.read_csv(csv_model_path)
    # changed_attributes_regex = '|'.join(changed_attributes)
    templates_with_changed_attributes = csv_model[
        csv_model["DependsOn"].isin(changed_attributes)
    ]["Attribute"].to_list()
    return templates_with_changed_attributes


def compare_template_module(
    current_templates_url: str, new_templates_path: str
) -> list:
    """Look at the current templates verses the existing template to find changed templates"""
    current_templates = pd.read_csv(current_templates_url, index_col=0)
    new_templates = pd.read_csv(new_templates_path, index_col=0)
    comp = new_templates.compare(current_templates, align_axis=0)
    changed_template_names = comp.index.get_level_values(0).to_list()

    return changed_template_names


def write_test_template_json(
    template_config_path: str, test_templates: set, output_file_path: str
):
    """Creates JSON of test templates"""
    with open(template_config_path, "r") as f:
        template_config = json.load(f)

    filtered_templates = [
        x
        for x in template_config["manifest_schemas"]
        if x["display_name"] in test_templates
    ]

    # ensures the file is closed after accessing it using a context manager
    with open(output_file_path, "w") as f:
        json.dump(filtered_templates, f)


def main(args):
    """Takes arguments from the user to generate test templates that have been changed."""

    with open(args.changed_files_path, "r", encoding="UTF-8") as file:
        changed_files = file

    changed_attributes = []
    changed_templates = []

    for x in changed_files:
        value = os.path.splitext(os.path.basename(x))[0]
        if value == "templates":
            changed_template_names = compare_template_module(
                args.current_templates_url, args.new_templates_path
            )
            changed_templates += changed_template_names
        else:
            changed_attributes.append(value)

    test_templates = set(
        changed_templates
        + get_templates_with_changed_attributes(args.csv_model_path, changed_attributes)
    )

    write_test_template_json(
        args.template_config_path, test_templates, args.output_file_path
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a JSON array of manifest templates with changes relative to adkp/data-model/main."
    )
    parser.add_argument(
        "--changed_files_path",
        help="path to changed-files.txt output of git diff --name-only",
        default="./tests/changed-files.txt",
    )
    parser.add_argument(
        "--current_templates_url",
        help="raw Github url to the currently in-use templates.csv attribute of the data model",
    )
    parser.add_argument(
        "--new_templates_path", help="path to modules/template/templates.csv"
    )
    parser.add_argument("--csv_model_path", help="path to csv data model")
    parser.add_argument(
        "--template_config_path", help="path to dca-template-config.json file"
    )
    parser.add_argument(
        "--output_file_path", help="path to write json file of manifests to generate"
    )

    args = parser.parse_args()

    main(args)
