
import pandas as pd
import numpy as np
import os

# ok so
# every valid value should inherit the module of its parent
# every module should get it's own ... 
# ok I think it should be like this
'''
Option1: each attribute + valid values gets its own csv under a module subfolder

data-models/
├── AD.model.csv
├── AD.model.jsonld
└── modules/
    ├── biospecimen/
    │   ├── specimenID.csv
    │   ├── organ.csv
    │   └── tissue.csv
    └── sequencing/
        ├── readLength.csv
        └── platform.csv
'''
# so a subdir named with the module
# then a csv for each attribute + its associated valid values, if any

# a function should take as input the csv of the data model
# and make a list of distinct modules in the module column
# and a list of all attributes where Parent = DataProperty
# check that subdirs for each module exist and if not make them
# for Parent = DataType, those all go in the template module, I think in one csv is best
# for the rest, each Parent = DataProperty should get its own csv
# and then anything with that attribute as Parent goes on the same csv
# and then that csv gets stored in the module subfolder


def split_data_model(csv_file):
    
    # Read the data model from the CSV 
    data_model = pd.read_csv("AD.model.csv")

    # Create a set of distinct modules
    modules = set(data_model['module'])

    # remove NaN values -- these will inherit from parent
    modules.discard(np.nan)

    # Create subdirectories for modules if they don't exist
    for module in modules:
        module_path = os.path.join('modules', module)
        os.makedirs(module_path, exist_ok=True)
        
        # Filter the data model for the current module
        module_data = data_model[data_model['module'] == module]

        # For DataProperty, create separate CSVs
        for attribute in module_data[module_data['Parent'] == 'ManifestColumn']['Attribute']:
            attribute_csv = os.path.join(module_path, f'{attribute}.csv')

            # term attribute
            attribute_data = module_data[module_data['Attribute'] == attribute]

            # any values with attribute as parent
            valid_vals = module_data[module_data['Parent'] == attribute]
            # alphabetize by value, ignoring case
            valid_vals.sort_values(by='Attribute', key=lambda col: col.str.lower()) 

            # combine into one csv
            pd.concat([attribute_data, valid_vals]).to_csv(attribute_csv, index = False)
        
        # Write manifest template attributes to a separate csv under the "template" module
        data_model[data_model['Parent'] == 'ManifestTemplate'].to_csv("modules/template/templates.csv", index = False)
    
if __name__ == "__main__":

    csv_file = 'AD.model.csv'
    split_data_model(csv_file)



