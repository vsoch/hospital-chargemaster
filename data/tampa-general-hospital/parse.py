#!/usr/bin/env python

import os
from glob import glob
import json
import pandas
import datetime

here = os.path.dirname(os.path.abspath(__file__))
folder = os.path.basename(here)
latest = '%s/latest' % here
year = datetime.datetime.today().year

output_data = os.path.join(here, 'data-latest.tsv')
output_year = os.path.join(here, 'data-%s.tsv' % year)

# Don't continue if we don't have latest folder
if not os.path.exists(latest):
    print('%s does not have parsed data.' % folder)
    sys.exit(0)

# Don't continue if we don't have results.json
results_json = os.path.join(latest, 'records.json')
if not os.path.exists(results_json):
    print('%s does not have results.json' % folder)
    sys.exit(1)

with open(results_json, 'r') as filey:
    results = json.loads(filey.read())

columns = ['charge_code', 
           'price', 
           'description', 
           'hospital_id', 
           'filename', 
           'charge_type']

df = pandas.DataFrame(columns=columns)

# First parse standard charges (doesn't have DRG header)
for result in results:
    filename = os.path.join(latest, result['filename'])
    if not os.path.exists(filename):
        print('%s is not found in latest folder.' % filename)
        continue

    if os.stat(filename).st_size == 0:
        print('%s is empty, skipping.' % filename)
        continue

    charge_type = 'standard'
    if "diagnosis" in filename.lower():
        charge_type = "drg"

    print("Parsing %s" % filename)

    if filename.endswith('xlsx'):

        if charge_type == "drg":

            # ['DRG', 'Charge']
            content = pandas.read_excel(filename, skiprows=1)

            for row in content.iterrows():

                entry = [row[1]['DRG'],                # charge code
                         row[1]['Charge'],             # price
                         None,                         # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         charge_type]            
                df.loc[idx,:] = entry

        else:

            # ['Tampa General Hospital - Hospital Service', 'Price']
            content = pandas.read_excel(filename)

            for row in content.iterrows():

                idx = df.shape[0] + 1
                if row[0] == 0:
                    continue

                # Each row has two hospitals!
                entry = [None,                                                # charge code
                         row[1]['Price'],                                     # price
                         row[1]['Tampa General Hospital - Hospital Service'], # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         charge_type]            
                df.loc[idx,:] = entry


# Remove empty rows
df = df.dropna(how='all')

# Save data!
print(df.shape)
df.to_csv(output_data, sep='\t', index=False)
df.to_csv(output_year, sep='\t', index=False)
