import pandas as pd
import numpy as np

# All DataProperty and DataType attributes have a manually designated "module" to help with organization
# All valid values of a DataProperty attribute (e.g. have that attribute as "Parent") should have the same module

# read in current data model
model = pd.read_csv("AD.model.csv")

# Read in manually assigned attribute modules.
updated_modules = pd.read_csv("manual_attribute_modules.csv")

# select just attribute and module columns
parent_modules = updated_modules[["Attribute", "UpdatedModule"]]

# join updated modules to current model 
joined_df = pd.merge(model, parent_modules, how = "left", on = "Attribute")

# replace NaN values with None type since they are strings
new_df = joined_df.where(pd.notnull(joined_df), None)

# loop over module values; if there is no module value for an attribute with a defined parent, module should be the parent's module
updated_module_list = []
for i, row in new_df.iterrows():
    if row["UpdatedModule"] is None:
        if row["Parent"] is not None:
            updated_module_list.append(joined_df.loc[joined_df["Attribute"] == joined_df.iloc[i]["Parent"]]["UpdatedModule"].values[0,])
        else: updated_module_list.append(None)
    else:
        updated_module_list.append(row["UpdatedModule"])

# add column to main model
new_df["FinalModules"] = updated_module_list

# drop unneeded columns
new_modules_df = new_df.drop(columns = ['module', 'UpdatedModule'])

# rename module column
new_modules_df = new_modules_df.rename(columns={"FinalModules": "module"})

# Write a new version of the ad data model. Will need to re-pull changes to get the new study that Amelia added
new_modules_df.to_csv("AD.model.csv", index = False)


