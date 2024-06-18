#!/usr/bin/env python

""" 
format_validation_rules.py: Format complex validation rules for schematic

USAGE: 
    python ./scripts/format_validation_rules.py \
    --yaml_file_path ./ID_attribute_validation_rules.yml \
    --assembled_model ./AD.model.csv \
    --output_path ./AD.test.model.csv
"""

__author__ = "Abby Vander Linden"
__status__ = "development"

import argparse
import yaml
import pandas as pd
from pathlib import Path


def load_yaml_file(yaml_file_path):
    """Load validation rules yaml file and return the data."""
    try:
        with open(yaml_file_path, 'r') as file:
            data = yaml.safe_load(file)
        return data
    except Exception as e:
        print(f"Error loading validation rules yaml file: {e}")


def transform_yaml_data(yaml_data):
    """Transform the yaml data into a DataFrame with attributes and validation rules."""
    attributes = []
    validation_rules = []

    try:
        attributes_data = yaml_data.get('attributes', [])
        if not attributes_data:
            raise ValueError("YAML incorrectly formatted for validation rules")

        for attribute in attributes_data:
            attribute_name = attribute.get('attribute')
            manifest_rules = []

            manifests = attribute.get('rules_applied_to_manifests', [])
            if not manifests:
                raise ValueError(f"No manifests found for attribute: {attribute_name}")

            for manifest in manifests:
                manifest_name = manifest.get('manifest')
                rule_string = '::'.join(manifest.get('rules', []))
                #level = manifest.get('level')
                #manifest_rule = f'#{manifest_name} {rule_string} {level}^^'
                manifest_rule = f'#{manifest_name} {rule_string}^^'
                manifest_rules.append(manifest_rule)

            if attribute_name:
                attributes.append(attribute_name)
                validation_rules.append(''.join(manifest_rules))

        if not attributes:
            raise ValueError("No attribute found in validation rule YAML.")

        transformed_df = pd.DataFrame({
            'Attribute': attributes,
            'Validation Rules': validation_rules
        })

        return transformed_df

    except KeyError as e:
        raise KeyError(f"Missing key in YAML data: {e}")
    except ValueError as e:
        raise ValueError(e)
    except Exception as e:
        raise Exception(f"An error occurred: {e}")


def update_data_model_validation_rules(rules_df, assembled_model):
    """Replace the validation rules in the main data model for attributes from the rules yaml"""
    model_df = pd.read_csv(assembled_model)
    merged_df = model_df.merge(rules_df, on = 'Attribute', how = 'left', suffixes = [None, '_new'])
    merged_df.loc[merged_df['Validation Rules_new'].notna(), 'Validation Rules'] = merged_df['Validation Rules_new']
    updated_df = merged_df.drop(columns = ['Validation Rules_new'])

    return updated_df


def save_to_csv(df, output_path):
    """Save DataFrame to a CSV file."""
    try:
        df.to_csv(output_path, index=False)
        print(f"Data model with updated validation rules saved to {output_path}")
    except Exception as e:
        print(f"Error saving updated model to CSV: {e}")

def main(args):
    """Main function to load YAML data, transform it, join to existing data model, and save updated model to a CSV file."""
    yaml_data = load_yaml_file(args.yaml_file_path)
    rules_df = transform_yaml_data(yaml_data)
    updated_model = update_data_model_validation_rules(rules_df, args.assembled_model)
    output_csv_path = args.output_path
    save_to_csv(updated_model, output_csv_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transform YAML data to a CSV format")
    parser.add_argument('--yaml_file_path', type=str, help='Path to the YAML file with validation rules')
    parser.add_argument('--assembled_model', type=str, help='Assembled csv data model')
    parser.add_argument('--output_path', type=str, help = 'Path to output updated data model csv with validation rules')
    args = parser.parse_args()

    main(args)
