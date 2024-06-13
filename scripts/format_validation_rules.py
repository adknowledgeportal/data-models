#!/usr/bin/env python

""" 
format_validation_rules.py: Format complex validation rules for schematic

USAGE: 
    python ./scripts/format_validation_rules.py \
    --yaml_file_path ./ID_attribute_validation_rules.yml \
    --output_path ./AD.test.model.csv
"""

__author__ = "Abby Vander Linden"
__status__ = "development"

import argparse
import yaml
import pandas as pd
import logging
from pathlib import Path


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_yaml_file(yaml_file_path):
    """Load validation rules yaml file and return the data."""
    try:
        with open(yaml_file_path, 'r') as file:
            data = yaml.safe_load(file)
        return data
    except Exception as e:
        logging.error(f"Error loading validation rules yaml file: {e}")
        raise

def transform_yaml_data(yaml_data):
    """Transform the yaml data into a DataFrame with attributes and validation rules."""
    attributes = []
    validation_rules = []

    for attribute in yaml_data.get('attributes', []):
        attribute_name = attribute.get('attribute')
        manifest_rules = []

        for manifest in attribute.get('rules_applied_to_manifests', []):
            manifest_name = manifest.get('manifest')
            rule_string = ' '.join(manifest.get('rules', []))
            level = manifest.get('level')
            manifest_rule = f'#{manifest_name} {rule_string} {level}^^'
            manifest_rules.append(manifest_rule)

        if attribute_name:
            attributes.append(attribute_name)
            validation_rules.append(''.join(manifest_rules))

    if not attributes:
        logging.warning("No attributes found in yaml data.")

    transformed_df = pd.DataFrame({
        'Attribute': attributes,
        'Validation Rules': validation_rules
    })

    return transformed_df

def save_to_csv(df, output_path):
    """Save DataFrame to a CSV file."""
    try:
        df.to_csv(output_path, index=False)
        logging.info(f"Transformed data saved to {output_path}")
    except Exception as e:
        logging.error(f"Error saving to CSV: {e}")
        raise

def main(yaml_file_path, output_path):
    """Main function to load YAML data, transform it, and save it to a CSV file."""
    yaml_data = load_yaml_file(yaml_file_path)
    transformed_df = transform_yaml_data(yaml_data)
    output_csv_path = output_path
    save_to_csv(transformed_df, output_csv_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transform YAML data to a CSV format")
    parser.add_argument('yaml_file', type=str, help='Path to the YAML file with validation rules')
    parser.add_argument('output_path', type=str, help = 'Path to output updated data model csv')
    args = parser.parse_args()

    try:
        main(args.yaml_file)
    except Exception as e:
        logging.error(f"Script execution failed: {e}")
