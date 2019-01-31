#!/usr/bin/env python

import os
from glob import glob
import json
import codecs
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

    print("Parsing %s" % filename)

    if filename.endswith('txt'):

        os.system('dos2unix %s' %filename)

        if "medications" in filename.lower():
            # NDC is national drug code, this may not be a charge code
            # Service Area|Px Code|Generic Name|CPT(R)/HCPCS Code|NDC|Unit Price|Override Bill Code|Override Price
            content = pandas.read_csv(filename, sep="|")
            for row in content.iterrows():
                idx = df.shape[0] + 1
                entry = [row[1]['CPT(R)/HCPCS Code'],   # charge code
                         row[1]['Unit Price'],         # price
                         row[1]['Generic Name'],    # description
                         result["hospital_id"],    # hospital_id
                         result['filename'],
                         'pharmacy']
                df.loc[idx,:] = entry

        elif "alternates" in filename.lower():
             # Service Area|Px Code|Procedure Description|Alternate CPT/HCPCS Code|Alternate Identification|Alternate Code by Location|Alternate Code by Department|Fee Schedule Group Name|Unit Price
            content = pandas.read_csv(filename, sep="|")
            for row in content.iterrows():
                idx = df.shape[0] + 1
                entry = [row[1]['Px Code'],                  # procedure code
                         row[1]['Unit Price'],               # price
                         row[1]['Procedure Description'],    # description
                         result["hospital_id"],    # hospital_id
                         result['filename'],
                         charge_type]
                df.loc[idx,:] = entry

        elif "procedures" in filename.lower():
             # Service Area|Px Code|Procedure Description|Default Rev Code|CPT(R)/HCPCS Code|Default Mod|Fee Schedule Group Name|Unit Price
            with codecs.open(filename, "r", encoding='utf-8', errors='ignore') as filey:
                lines = filey.readlines()[1:]
            for line in lines:
                idx = df.shape[0] + 1
                line=line.strip('\n').split('|')
                entry = [line[1],                  # charge code
                         line[-1].replace(',',''), # price
                         line[2],    # description
                         result["hospital_id"],    # hospital_id
                         result['filename'],
                         charge_type]
                df.loc[idx,:] = entry

        elif "supplies" in filename.lower():
            with codecs.open(filename, "r", encoding='utf-8', errors='ignore') as filey:
                lines = filey.readlines()[1:]
            # Service Area|Px Code|Procedure Description|Supply #|Unit Price
            for line in lines:
                idx = df.shape[0] + 1
                line=line.strip('\n').split('|')
                entry = [line[1],                  # charge code
                         line[-1].replace(',',''), # price
                         line[2],    # description
                         result["hospital_id"],    # hospital_id
                         result['filename'],
                         charge_type]
                df.loc[idx,:] = entry

        else:
            print('Skipping %s' %filename)   

# Remove empty rows
df = df.dropna(how='all')

# Save data!
print(df.shape)
df.to_csv(output_data, sep='\t', index=False)
df.to_csv(output_year, sep='\t', index=False)
