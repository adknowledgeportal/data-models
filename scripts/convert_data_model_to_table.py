# %%
import synapseclient
import synapseutils
from synapseclient import Project, File, Folder
from synapseclient import Schema, Column, Table, Row, RowSet, as_table_columns
import pandas as pd
import itertools

# %%
syn = synapseclient.Synapse()
syn.login()

# %%
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# %%
# read in AD data model from Github
ad_model_df = pd.read_csv('https://raw.githubusercontent.com/adknowledgeportal/data-models/main/AD.model.csv')

# %%
# add "admID" column to uniquely identify rows and explode DataFrame on "Valid Values" column
# to obtain rows containing unique (key, valid value) pairs
ad_model_df['admID'] = ad_model_df.index.astype(str)
ad_model_df['admID'] = ad_model_df['admID'].map(lambda x: 'adm' + x.zfill(8))

if (type(ad_model_df['Valid Values'][0]) != str):
    del ad_model_df
    ad_model_df = pd.read_csv('https://raw.githubusercontent.com/adknowledgeportal/data-models/main/AD.model.csv')
    ad_model_df['Valid Values'] = ad_model_df['Valid Values'].str.split(",")
    new_df = ad_model_df.explode('Valid Values', ignore_index=True)

# %%
# find all valid values to drop the rows where "Attribute" is one of the valid values
mega = ",".join(ad_model_df['Valid Values'].astype(str))
valid_vals = new_df['Valid Values'].astype(str).map(lambda x: x.lstrip()).tolist()
valid_vals = [x for x in valid_vals if str(x) != 'nan']

# %%
# map values to descriptions and value descriptions
values = [x for x in ad_model_df['Attribute'].astype(str).tolist() 
          if x not in ad_model_df['Parent'].astype(str).tolist()]

atbr_to_desc = dict(zip(ad_model_df['Attribute'], ad_model_df['Description']))

val_to_desc = {x: atbr_to_desc.get(x) for x in values if x not in valid_vals}
val_to_val_desc = {x: atbr_to_desc.get(x) for x in values if x in valid_vals}

# %%
# fill in value description column conditionally
new_df['valueDescription'] = ''

new_df['Valid Values'] = new_df['Valid Values'].astype(str).map(lambda x: x.lstrip())

for atr in new_df['Valid Values'].astype(str).tolist():
    if atr in valid_vals:
        new_df.loc[new_df['Valid Values'] == atr, 'valueDescription'] = atbr_to_desc.get(atr)

# %%
# drop rows where attribute is a valid value
attributes = new_df['Attribute'].astype(str).tolist()
atrb_in_vv = [a for a in attributes if a in valid_vals]

fin_df = new_df[~new_df['Attribute'].isin(atrb_in_vv)]
fin_df = fin_df.reset_index(drop=True)

# %%
# set columns in DataFrame table representing syn53010627 equal to corresponding ones in fin_df
annotation_modules_schema = syn.get('syn53010627')
annotation_modules_results = syn.tableQuery(f"SELECT * from {annotation_modules_schema.id}")
annotation_modules_df = pd.read_csv(annotation_modules_results.filepath)

annotation_modules_df['key'] = fin_df['Attribute']
annotation_modules_df['description'] = fin_df['Description']
annotation_modules_df['columnType'] = fin_df['columnType']
annotation_modules_df['value'] = fin_df['Valid Values']
annotation_modules_df['valueDescription'] = fin_df['valueDescription']
annotation_modules_df['source'] = fin_df['Source']
annotation_modules_df['module'] = fin_df['module']

# %%
# normalize missing values across table
annotation_modules_df.loc[annotation_modules_df['value'] == 'nan', 'value'] = ''
annotation_modules_df.loc[annotation_modules_df['description'].isna(), 'description'] = ''
annotation_modules_df.loc[annotation_modules_df['columnType'].isna(), 'columnType'] = ''
annotation_modules_df.loc[annotation_modules_df['maximumSize'].isna(), 'maximumSize'] = ''
annotation_modules_df.loc[annotation_modules_df['valueDescription'].isna(), 'valueDescription'] = ''
annotation_modules_df.loc[annotation_modules_df['source'].isna(), 'source'] = ''
annotation_modules_df.loc[annotation_modules_df['module'].isna(), 'module'] = ''


annotation_modules_df.loc[annotation_modules_df['columnType'] == 'boolean', 'value'] = 'True, False'

annotation_modules_df.drop_duplicates(keep='first', inplace=True, ignore_index=True)

# %%
#init_len = 1284
# fin_len = 1278... we lost 6 total rows which is consistent with expectations
syn.store(Table('syn53010627', annotation_modules_df))