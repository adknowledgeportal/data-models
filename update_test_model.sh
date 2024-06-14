#!/bin/bash

# assemble full csv model from current module csv
python scripts/assemble_csv_data_model.py modules AD.model.csv

# add formatted validation rules
python ./scripts/format_validation_rules.py --yaml_file_path ID_attribute_validation_rules.yml --assembled_model AD.model.csv --output_path AD.test.model.csv

# convert to json-ld
schematic schema convert AD.test.model.csv
