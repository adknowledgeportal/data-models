# testing process: generate the individual metadata template, fill, submit; 
# generate biospecimen template, fill a pass and fail version, and validate to check rule
# this script is not executable, I copied and pasted
# I just like the bash color formatting

# update pyenv venv schematic-latest to use 24.4.1

# assemble csv model
python scripts/assemble_csv_data_model.py modules AD.model.csv

# convert to jsonld
schematic schema convert AD.model.csv

# generate individual human metadata manifest
schematic manifest -c xman-testing-config.yml get -dt IndividualHumanMetadataTemplate -o csv-manifests/individual.csv -oxlsx excel-manifests/individual.xlsx

# fill the manifest in excel, save, and validate
schematic model -c xman-testing-config.yml validate -mp filled-manifests/individual_filled_pass.csv -dt IndividualHumanMetadataTemplate

# submit valid manifest
schematic model -c xman-testing-config.yml submit -mp filled-manifests/individual_filled_pass.csv -d syn58710314 -mrt file_only

# generate biospecimen manifest
schematic manifest -c xman-testing-config.yml get -dt BiospecimenMetadataTemplate -o csv-manifests/biospecimen.csv -oxlsx excel-manifests/biospecimen.xlsx

# filled a biospecimen manifest with one individualID that IS in the submitted individual metadata template
# now validate
schematic model -c xman-testing-config.yml validate -mp filled-manifests/biospecimen_filled_pass_1.csv -dt BiospecimenMetadataTemplate

# validate a fail biospecimen manifest -- one individualID is in submitted individual metadata template, and one is not
schematic model -c xman-testing-config.yml validate -mp filled-manifests/biospecimen_filled_fail_1.csv -dt BiospecimenMetadataTemplate