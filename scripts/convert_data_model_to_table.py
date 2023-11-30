""" Convert AD data model, the raw Github link to which is 
provided as a command-line argument, to a flattened Synapse 
table matching the schema of the formerly-used 
Annotation Modules (syn10242922) table.

author: victor.baham
"""


import argparse
import synapseclient
from synapseclient import Project, File, Folder
from synapseclient import Schema, Column, Table, Row, RowSet, as_table_columns
import pandas as pd

syn = synapseclient.Synapse()
syn.login()

def get_args():
    """This function gets the Synapse tables to be 
    processed from command line arguments."""
    parser = argparse.ArgumentParser(
        description="Flatten data model into Synapse table")
    parser.add_argument("-d", "--data_model",
                        type=str, default="https://raw.githubusercontent.com/adknowledgeportal/data-models/main/AD.model.csv",
                        help="URL to raw AD data model file.")
    parser.add_argument("--dryrun", action="store_true")
    return parser.parse_args()

def explode_and_remake(adm_df):
    # if the type of the 'Valid Values' column is not 'str', delete the DataFrame
    # otherwise, explode the DataFrame on the "Valid Values" column
    # to obtain rows containing unique (key, valid value) pairs

    if (type(adm_df['Valid Values'][0]) != str):
        del adm_df
        adm_df = pd.read_csv('https://raw.githubusercontent.com/adknowledgeportal/data-models/main/AD.model.csv')
        adm_df['Valid Values'] = adm_df['Valid Values'].str.split(",")
        new_df = adm_df.explode('Valid Values', ignore_index=True)

    return new_df
    
def extract_and_emphasize(adm_df, n_df):
    # convert 'Valid Values' column to type 'str' and strip the
    # extra whitespace to the left of each non-NaN term
    valid_vals = n_df['Valid Values'].astype(str).map(lambda x: x.lstrip()).tolist()
    valid_vals = [x for x in valid_vals if str(x) != 'nan']

    # map values to descriptions and value descriptions
    atbr_to_desc = dict(zip(adm_df['Attribute'], adm_df['Description']))

    # create and fill in value description column conditionally
    # if the value in the exploded 'Valid Values' column is in 
    # valid_vals, then it needs a corresponding entry in the 
    # 'valueDescription' column
    n_df['valueDescription'] = ''

    n_df['Valid Values'] = n_df['Valid Values'].astype(str).map(lambda x: x.lstrip())

    for atr in n_df['Valid Values'].astype(str).tolist():
        if atr in valid_vals:
            n_df.loc[n_df['Valid Values'] == atr, 'valueDescription'] = atbr_to_desc.get(atr)

    # drop rows where attribute is a valid value
    attributes = n_df['Attribute'].astype(str).tolist()
    atrb_in_vv = [a for a in attributes if a in valid_vals]

    fin_df = n_df[~n_df['Attribute'].isin(atrb_in_vv)]
    fin_df = fin_df.reset_index(drop=True)

    return fin_df

def finalize_table(fin_df):
    # set columns in DataFrame table representing syn53010627 equal to corresponding ones in fin_df
    anm_df_schema = syn.get('syn53010627')
    anm_df_results = syn.tableQuery(f"SELECT * from {anm_df_schema.id}")
    anm_df = pd.read_csv(anm_df_results.filepath)

    anm_df['key'] = fin_df['Attribute']
    anm_df['description'] = fin_df['Description']
    anm_df['columnType'] = fin_df['columnType']
    anm_df['value'] = fin_df['Valid Values']
    anm_df['valueDescription'] = fin_df['valueDescription']
    anm_df['source'] = fin_df['Source']
    anm_df['module'] = fin_df['module']

    # normalize missing values across table

    # the 'value' column needs its own handling since it was converted to 'str' type earlier
    anm_df.loc[anm_df['value'] == 'nan', 'value'] = ''

    # the others can be handled in a loop; for each applicable column in the DataFrame,
    # replace null values with the empty string ''
    anm_cols = ['description', 'columnType', 'maximumSize', 
                'valueDescription', 'source','module']
    
    for anm_col in anm_cols:
        anm_df.loc[anm_df[anm_col].isna(), anm_col] = ''

    # merge back exploded rows where boolean values were split
    anm_df.loc[anm_df['columnType'] == 'boolean', 'value'] = 'True, False'
    anm_df.drop_duplicates(keep='first', inplace=True, ignore_index=True)

    return anm_df

def main():
    # get args from command-line
    args = get_args() 
    data_model_url = args.data_model

    # successively call necessary functions on command-line input
    ad_model_df = pd.read_csv(data_model_url)
    exploded_am_df = explode_and_remake(ad_model_df)
    intermediate_df = extract_and_emphasize(ad_model_df, exploded_am_df)
    final_df = finalize_table(intermediate_df)

    # make user confirm they want to store changes
    user_confirm = input("Are you sure you want to store these changes to syn53010627? (y for yes/n for no)")

    if user_confirm == "y":
        syn.store(Table('syn53010627', final_df))
    elif user_confirm == "n":
        pass

if __name__ == "__main__":
    main()