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

#### try again with component for individual id

# submit valid manifest
schematic model -c xman-testing-config.yml submit -mp filled-manifests/individual_human_with_component_filled_pass.csv -d syn58710314 -mrt file_only

# generate biospecimen manifest
schematic manifest -c xman-testing-config.yml get -dt BiospecimenMetadataTemplate -o csv-manifests/biospecimen.csv -s

# validation biospecimen -- how does it know what to validate against? I forsee problems with the project scope issue ... 
schematic model -c xman-testing-config.yml validate -mp filled-manifests/biospecimen_with_component_filled_pass.csv -dt BiospecimenMetadataTemplate

# getting this error even after the individual manifest above was submitted, so I don't think the component validation is working
warning: Cross Manifest Validation Warning: There are no target columns to validate this manifest against for attribute: individualID, and validation rule: matchAtLeastOne IndividualComponent.individualID value error. It is assumed this is the first manifest in a series to be submitted, so validation will pass, for now, and will run again when there are manifests uploaded to validate against.
Your manifest has been validated successfully. There are no errors in your manifest, and it can be submitted without any modifications.



### testing with new validation rules
# updated x-man testing config to point to AD.test.model.jsonld for these tests

# generate individual human metadata manifest
schematic manifest -c xman-testing-config.yml get -dt IndividualHumanMetadataTemplate -o csv-manifests/individual_human_x.csv -oxlsx excel-manifests/individual_human_x.xlsx

# generate individual key
schematic manifest -c xman-testing-config.yml get -dt IndividualKey -o csv-manifests/individual_key.csv -oxlsx excel-manifests/individual_key.xlsx

# validate individual key
schematic model -c xman-testing-config.yml validate -mp filled-manifests/individual_key_filled.csv -dt IndividualKey

# submit individual key to individual key folder
schematic model -c xman-testing-config.yml submit -mp filled-manifests/individual_key_filled.csv -d syn61053035 -mrt file_only

# validate individual human metadata
# should  - individualIDs all in IndividualKey
# passed!
schematic model -c xman-testing-config.yml validate -mp filled-manifests/individual_human_filled_pass.csv -dt IndividualHumanMetadataTemplate

# submit it
schematic model -c xman-testing-config.yml submit -mp filled-manifests/individual_human_filled_pass.csv -d syn58710314 -mrt file_only

# try some failure cases:

# note: I think rule combinations with unique, cross-manifest rules, and regex matching aren't working
# temp solution is to prioritize "unique" for the individual and specimen keys and not worry about the matchNone and the regex

# also gotta force the asset view to requery after uploading a manifest

# 1: individual metadata missing id found in individual key - 
# would like this to fail but it won't because we're using "value" instead of "set"
# no failure
# still no failure even with :: formatting on "set", seems like some kind of bug
schematic model -c xman-testing-config.yml validate -mp filled-manifests/individual_human_filled_fail_missing_id_from_key.csv -dt IndividualHumanMetadataTemplate


# 2: individual metadata has id not in individual key - 
# should have failed, didn't. 
# the first time I tried it found the individual id key but didn't flag the error of missing id/ non complete set
# the second time it didn't find any manifests that fit the basename -- specifically didn't look in the dataset with the key manifest
# is that a synapse cache thing?
# try commenting out the "unique" rule
# still no error
# tried clearing the synapse cache
# it did re-download the existing key manifest but still not throwing a cross-manifest error as expected
# oh my gooddddddd was it that the target attribute was written .individualID and not .IndividualID???
# nope, still no error
# clear the synapse cache again
# nope, still no error
# try removing the warning/error level flag entirely
# still no error
# try removing the required rule so there's just the single cross-manifest rule
# nope
# scope matchExactlyOne to "value" rather than "set"
# ok THAT finally got it
schematic model -c xman-testing-config.yml validate -mp filled-manifests/individual_human_filled_fail_id_not_in_key.csv -dt IndividualHumanMetadataTemplate

# 3: individual metadata has non-unique ids
# no errors and should have had errors
# didn't work -- removed test case since can't combine unique with cross-manifest validation
# this is currently a concern because the "set" scope isn't working either
# works -- triggering a duplicate value error
schematic model -c xman-testing-config.yml validate -mp filled-manifests/individual_human_filled_fail_id_not_unique.csv -dt IndividualHumanMetadataTemplate


#5: individual human metadata has row missing individualID, which should be required
# failed as expected
# "too short" is a non-intuitive error message, though
# still works even with matchExactlyOne is combined with unique and then required -- unique not interrupting required, just not getting used
# now works! triggering "too short" error
schematic model -c xman-testing-config.yml validate -mp filled-manifests/individual_human_filled_fail_missing_required_id.csv -dt IndividualHumanMetadataTemplate

# 4: individual key has non-valid ID - fail
# only error is the non-unique -- should have triggered a matchNone error with the previously submitted manifest, and a not-allowed character
# might be that they have to go in different dataset folders, dangit
# ok, removing the rule combination for this manifest produced the expected failure for duplicates
# this is probably the most important
# the human metadata is lookign for a set with this manfiest so that should help avoid duplicates in the individual metadata
# ^update, can't rely on that
# still triggers non-unique error
# update: does not trigger, KeyError in validation code from schematic (can't parse the regex apart from the other rules)
schematic model -c xman-testing-config.yml validate -mp filled-manifests/individual_key_filled_fail_not_unique.csv -dt IndividualKey

#6. individual key has disallowed characters 
# do the unique and regex match rules work in combination?
# no trigger on the regex match, which should have failed this one
schematic model -c xman-testing-config.yml validate -mp filled-manifests/individual_key_filled_fail_regex_match.csv -dt IndividualKey

####TODO:

# other individualID testing:
# individual animal template

# individual model ad template
# generate template
schematic manifest -c xman-testing-config.yml get -dt IndividualAnimalMODEL-ADMetadataTemplate -o csv-manifests/modelad_individual.csv -oxlsx excel-manifests/modelad_individual.xlsx

# This needs a new synapse project, if I try to upload it to the existing project it should fail (will validate against the human individualID key)
# test this behavior: upload to "human test study A" project to see if there is an issue
schematic model -c xman-testing-config.yml validate -mp filled-manifests/modelad_individual_filled_pass.csv -dt  IndividualAnimalMODEL-ADMetadataTemplate
#^ that failed -- tried to validate against the previously submitted human key, which didn't match
# submit a mouse individual key
# first need to create a mouse individual key folder
schematic model -c xman-testing-config.yml submit -mp filled-manifests/modelad_individual_key_filled.csv -d syn61463641 -mrt file_only
# now validate -- see if it fails against the human or succeeds against the mouse
schematic model -c xman-testing-config.yml validate -mp filled-manifests/modelad_individual_filled_pass.csv -dt  IndividualAnimalMODEL-ADMetadataTemplate
#^ successfully validated -- must have found the mouse key. So they don't HAVE to be in separate projects to validate correctly

#upload individual manifest to model ad individual study folder
schematic model -c xman-testing-config.yml submit -mp filled-manifests/modelad_individual_filled_pass.csv -d syn61463506 -mrt file_only


# moved to a separate project
# now confirm specimen key and biospecimen file work
schematic manifest -c xman-testing-config.yml get -dt SpecimenKey -oxlsx excel-manifests/specimen_key.xlsx
# submit to dataset folder in separate project
schematic model -c xman-testing-config.yml submit -mp filled-manifests/modelad_specimen_key_filled_pass.csv -d syn61464463 -mrt file_only
#^ this actually should have failed -- there's a non-unique value
# rename to "fail" and try again
schematic model -c xman-testing-config.yml validate -mp filled-manifests/modelad_specimen_key_filled_fail_not_unique.csv -dt SpecimenKey
# we get the expected failure -- validation rule must have been formatted incorrectly

# submit corrected pass manifest
schematic model -c xman-testing-config.yml submit -mp filled-manifests/modelad_specimen_key_filled_pass.csv -d syn61464463 -mrt file_only

# testing biospecimen file -- 
# pass: all individualIDs in individualkey, all specimenIDs in specimenkey, all specimen IDs unique
schematic model -c xman-testing-config.yml validate -mp filled-manifests/modelad_biospecimen_filled_pass.csv -dt BiospecimenMetadataTemplate
schematic model -c xman-testing-config.yml submit -mp filled-manifests/modelad_biospecimen_filled_pass.csv -d syn61464458 -mrt file_only
#^ successfully submitted

# biospecimen fail: individualIDs in more than one manifest
# e.g., what happens if I mess up and there's an individualID from a different study's manifest -- matchExactlyOne should be violated
schematic model -c xman-testing-config.yml validate -mp filled-manifests/modelad_biospecimen_filled_fail_match_more_than_one_manifest.csv -dt BiospecimenMetadataTemplate
#^this does trigger an error that it doesn't match just one other manifest -- I think that's good! enforces no overlap between studies if we set things up correctly
# "error: Value(s) ['234567_DLPFC_01'] from row(s) ['5'] of the attribute specimenID in the source manifest are not present in only one other manifest. "
# ^only problem is that is impossible to distinguish from "not present at all" vs "present in more than one manifest"

# biospecimen fail - specimenID not unique
schematic model -c xman-testing-config.yml validate -mp filled-manifests/modelad_biospecimen_filled_fail_spec_not_unique.csv -dt BiospecimenMetadataTemplate
#^ failed as expected

# biospecimen fail - individualID not in individualKey
schematic model -c xman-testing-config.yml validate -mp filled-manifests/modelad_biospecimen_filled_fail_ind_not_in_key.csv -dt BiospecimenMetadataTemplate
# failed as expected

# biospecimen fail - specimenID not provided (missing)
schematic model -c xman-testing-config.yml validate -mp filled-manifests/modelad_biospecimen_filled_fail_missing_specID.csv -dt BiospecimenMetadataTemplate
# failed as expected



# MRI template
# PET template
schematic manifest -c xman-testing-config.yml get -dt AssayPETMetadataTemplate -oxlsx excel-manifests/PET_assay_metadata.xlsx
# validate and submit the pass version
schematic model -c xman-testing-config.yml validate -mp filled-manifests/modelad_PET_metadata_filled_pass.csv -dt AssayPETMetadataTemplate
# all good
schematic model -c xman-testing-config.yml submit -mp filled-manifests/modelad_PET_metadata_filled_pass.csv -d syn61464459 -mrt file_only

# PET fail -- individualID not in individualKey
schematic model -c xman-testing-config.yml validate -mp filled-manifests/modelad_PET_metadata_filled_fail_indID_not_in_key.csv -dt AssayPETMetadataTemplate
# failed as expected

# autorad template

---
# moving on -- biospecimen pass/fail

# specimen key pass
# biospecimen metadata against specimenkey
# biospecimen metadata against individualkey
# in vitro biospecimen metadata against specimenkey
# in vitro biospecimen against individualkey
# assay metadata against specimenkey

--- 

### testing file annotation templates
# get template for fake RNAseq files in human study A
schematic manifest -c xman-testing-config.yml get -dt FileAnnotationTemplate -d syn58710382 -oxlsx excel-manifests/human_study_a_rnaseq_raw_file_manifest.xlsx

# need specimen key and biospecimen metadata for human study as well
schematic model -c xman-testing-config.yml submit -mp filled-manifests/biospecimen_filled_pass.csv -d syn58710329 -mrt file_only
# ^submitting this first, it may not have specimenIDs to match against so should get that as a message
# did not get that as a message, maybe because I went straight to submit first? instead of validate
schematic model -c xman-testing-config.yml submit -mp filled-manifests/specimen_key_filled_pass.csv -d syn61053095 -mrt file_only
# ok both submitted

# now try validating file annotation manifest: pass
schematic model -c xman-testing-config.yml validate -mp filled-manifests/human_study_a_rnaseq_raw_file_filled_pass.csv -dt FileAnnotationTemplate 
# passed as expected

# file annotation: failures
# individualID not in individualID key, specimenID not in specimen key
schematic model -c xman-testing-config.yml validate -mp filled-manifests/human_study_a_rnaseq_raw_file_filled_fail_IDs_not_in_key.csv -dt FileAnnotationTemplate 
# good - both failed

# submit and check that annotations are applied

schematic model -c xman-testing-config.yml submit -mp filled-manifests/human_study_a_rnaseq_raw_file_filled_pass.csv -d syn58710382 -mrt file_only


#other:
# test protect ages
# human individual metadata only one where ageDeath is protected
# test uncensored age over 90
schematic model -c xman-testing-config.yml validate -mp filled-manifests/individual_human_filled_fail_age_over_90.csv -dt IndividualHumanMetadataTemplate
# doesn't work if the contributor has already self-censored with a non-numeric character - removing for now and we will have to verify
