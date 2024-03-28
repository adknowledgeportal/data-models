
import os
import pandas as pd
import json
import argparse


def get_templates_with_changed_attributes(csv_model_path: str, changed_attributes:list) -> list:
    csv_model = pd.read_csv(csv_model_path)
    changed_attributes_regex = '|'.join(changed_attributes)
    templates_with_changed_attributes = csv_model[csv_model['DependsOn'].str.contains(changed_attributes_regex, na = False)]['Attribute'].to_list()
    return templates_with_changed_attributes


def compare_template_module(current_templates_url: str, new_templates_path: str) -> list:
    current_templates = pd.read_csv(current_templates_url, index_col = 0)
    new_templates = pd.read_csv(new_templates_path, index_col = 0)
    comp = new_templates.compare(current_templates, align_axis = 0)
    changed_template_names = comp.index.get_level_values(0).to_list()
    return changed_template_names


def write_test_template_json(template_config_path: str, test_templates: set, output_file_path: str):
    template_config = json.load(open(template_config_path))
    filtered_templates = [x for x in template_config['manifest_schemas'] if (x['display_name']) in (test_templates)]
    file = open(output_file_path, "w")
    json.dump(filtered_templates, file)


def main(args):

    changed_files_path = args.changed_files_path
    current_templates_url = args.current_templates_url
    new_templates_path = args.new_templates_path
    csv_model_path = args.csv_model_path
    template_config_path = args.template_config_path
    output_file_path = args.output_file_path

    changed_files = open(changed_files_path, 'r')

    changed_attributes = list()
    changed_templates = list()

    for x in changed_files:
        value = os.path.splitext(os.path.basename(x))[0]
        if value == 'templates' :
            changed_template_names = compare_template_module(current_templates_url, new_templates_path)
            changed_templates = changed_templates + changed_template_names
        else: 
            changed_attributes.append(value)

    test_templates = set(changed_templates + 
                        get_templates_with_changed_attributes(csv_model_path, changed_attributes))

    write_test_template_json(template_config_path, test_templates, output_file_path)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a JSON array of manifest templates with changes relative to adkp/data-model/main.")
    parser.add_argument("--changed_files_path", help="path to changed-files.txt output of git diff --name-only", default="./tests/changed-files.txt")
    parser.add_argument("--current_templates_url", help="raw Github url to the currently in-use templates.csv attribute of the data model")
    parser.add_argument("--new_templates_path", help="path to modules/template/templates.csv")
    parser.add_argument("--csv_model_path", help="path to csv data model")
    parser.add_argument("--template_config_path", help="path to dca-template-config.json file")
    parser.add_argument("--output_file_path", help="path to write json file of manifests to generate")

    args = parser.parse_args()
    main(args)
