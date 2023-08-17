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

# grab a template schema with no required columns for testing
no_req_file = open(list(filter(lambda name: '16S' in name, file_paths))[0])
no_req_json = json.load(no_req_file)


def append_required(required_list, json_stuff):

    if 'required' in json_stuff:
        required_list.append(json_stuff['required'])
    else: 
        required_list.append(None)    


# open the file
a_file = open(file_paths[1])

# read the json
some_json = json.load(a_file)

# create data frame of attributes representing metadata templates, i.e. Parent = "DataType"
def createTemplateDataFrame(file_path_list):

    # actually do do lists
    attribute = list()
    schema_id = list()
    description = list()
    dependsOn = list()
    csv_properties = list() # properties column in csv, not properties defined in json schema
    schema_required_columns = list() # store as an additional column for later
    template_required = list()
    valid_values = list()
    parent = list()
    dependsOn_component = list()
    validation_rules = list()

    # loop over the file paths of the metadata template json schemas
    for file_name in file_path_list:

        # open the file and read the json
        file = open(file_name)
        json_schema = json.load(file)

        # populate lists with values from each template schema
        attribute.append(os.path.basename(json_schema).replace('.json', ''))
        schema_id.append(json_schema['$id'])
        description.append(json_schema['description'])
        dependsOn.append(', '.join(json_schema['properties']))
        csv_properties.append(None)
        append_required(schema_required_columns, json_schema)
        template_required.append('FALSE')
        valid_values.append(None)
        parent.append('DataType')
        dependsOn_component.append(None)
        validation_rules.append(None)

    # make the data frame
    df = pd.DataFrame({'Attribute': attribute, 
                   'Description': description, 
                   'Valid Values': valid_values, 
                   'DependsOn': dependsOn, 
                   'Properties': csv_properties, 
                   'Required': template_required,
                   'Parent': parent,
                   'DependsOn Component': dependsOn_component,
                   'Source': schema_id,
                   'Validation Rules': validation_rules,
                   'Schema Required Columns': schema_required_columns}, 
                   index=[0])
    
    return(df)
    
    
# create data frame of attributes representing template columns, i.e. Parent = 'DataProperty'
column_attribute = list(properties)
column_source = list(pd.DataFrame.from_dict(properties.values())['$ref'])
column_required = list()
for item in column_attribute:
    if required is not None and item in required:
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
