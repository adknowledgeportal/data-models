import os
import json
import synapseclient
import pandas as pd

syn = synapseclient.Synapse()
syn.login(authToken=os.environ.get('SYNAPSE_PAT'))

# read in metadata templates and convert to ... data frame?

# list files in directory

path = 'schema_metadata_templates/'


def getFullPaths(directory):
    full_paths = list()
    for root, dirs, files in os.walk(os.path.abspath(path)):
        for file in files:
            full_paths.append(os.path.join(root, file))
    return full_paths


file_paths = getFullPaths(path)

# open the file
a_file = open(file_paths[1])

# read the json
some_json = json.load(a_file)

# can I index the json? yes because it's a dict
type(some_json)

dir(some_json)
some_json.keys()

# create values for schema.org csv format for 'DataType' attributes i.e. templates
schema_id = some_json['$id']
description = some_json['description']
properties = some_json['properties']
dependsOn = ', '.join(list(properties))
required = some_json['required'] if some_json['required'] is not None else None
attribute = os.path.basename(file_paths[1]).replace('.json', '')


df = pd.DataFrame({'Attribute': attribute, 
                   'Description': description, 
                   'Valid Values': None, 
                   'DependsOn': dependsOn, 
                   'Properties': None, 
                   'Required': 'FALSE', 
                   'Parent': 'DataType', 
                   'DependsOn Component': None, 
                   'Source': schema_id,
                   'Validation Rules': None}, 
                   index=[0])

column_attribute = list(properties)
column_source = list(pd.DataFrame.from_dict(properties.values())['$ref'])
column_required = list()
for item in column_attribute:
    if item in required:
        column_required.append('TRUE')
    else:
        column_required.append('FALSE')

df_also = pd.DataFrame({'Attribute': column_attribute, 
                   'Description': None, 
                   'Valid Values': None, 
                   'DependsOn': None, 
                   'Properties': None, 
                   'Required': column_required, 
                   'Parent': 'DataProperty', 
                   'DependsOn Component': None, 
                   'Source': column_source,
                   'Validation Rules': None})

basic_model = pd.concat([df, df_also], ignore_index = True)
