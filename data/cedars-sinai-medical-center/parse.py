#!/usr/bin/env python

import os
from glob import glob
import json
import pandas
import codecs
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

    print("Parsing %s" % filename)

    charge_type = 'standard'
    if "drg" in filename:
        charge_type = 'drg'

    # This is a file of procedure counts
    elif "procedures" in filename:
        print('%s has procedures counts, not charges.' %filename)

    print("Parsing %s" % filename)

    if filename.endswith('xlsx'):

        if charge_type == "drg":

            # ['MS DRG Code', 'MS DRG Description', 'Average Charge']
            content = pandas.read_excel(filename, skiprows=4)

            for row in content.iterrows():
                idx = df.shape[0] + 1
                entry = [row[1]['MS DRG Code'],        # charge code
                         row[1]['Average Charge'],     # price
                         row[1]['MS DRG Description'], # description
                         result["hospital_id"],     # hospital_id
                         result['filename'],
                         charge_type]                 
                df.loc[idx,:] = entry


        elif charge_type == "standard":
            # Newlines in column field names... :/
            # https://en.wikipedia.org/wiki/Healthcare_Common_Procedure_Coding_System
            # IP probably means inpatient, or ER
            # OP --> outpatient, default
            # ['Charge\nCode', 'Description', 'CPT/ HCPCS\nCode', 'OP/ Default Price', 'IP/ER\nPrice']
            content = pandas.read_excel(filename, skiprows=3)
   
            for row in content.iterrows():
                outpatient = row[1]['OP/ Default Price']
                inpatient = row[1]['IP/ER\nPrice']

                # Add outpatient, if not null
                if not pandas.isnull(outpatient):
                    idx = df.shape[0] + 1
                    entry = [row[1]['Charge\nCode'],      # charge code
                             outpatient,                  # price
                             row[1].Description,          # description
                             result["hospital_id"],       # hospital_id
                             result['filename'],
                             'outpatient']                # filename
                    df.loc[idx,:] = entry

                if not pandas.isnull(inpatient):
                    idx = df.shape[0] + 1
                    entry = [row[1]['Charge\nCode'],      # charge code
                             inpatient,                   # price
                             row[1].Description,          # description
                             result["hospital_id"],       # hospital_id
                             result['filename'],
                             'inpatient']                 # filename
                    df.loc[idx,:] = entry


# Remove empty rows
df = df.dropna(how='all')

# Save data!
print(df.shape)
df.to_csv(output_data, sep='\t', index=False)
df.to_csv(output_year, sep='\t', index=False)
