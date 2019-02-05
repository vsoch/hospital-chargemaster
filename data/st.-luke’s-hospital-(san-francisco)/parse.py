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

    if filename.endswith('json'):

         with codecs.open(filename, "r", encoding='utf-8-sig', errors='ignore') as filey:
             content = json.loads(filey.read())

         charge_types = {'DRG': 'drg', 
                         'IP': 'inpatient', 
                         'OP': 'outpatient', 
                         'RX': 'pharmacy', 
                         'SUP': 'supply'}

         for row in content['CDM']:
            hospital = result["hospital_id"]
            if 'HOSPITAL_NAME' in row:
                hospital = row['HOSPITAL_NAME']
            description_key = 'DESCRIPTION'
            if description_key not in row:
                description_key = 'DESCRIPION'
            charge_type = charge_types[row['SERVICE_SETTING']]
            idx = df.shape[0] + 1
            entry = [row['CDM'],              # charge code
                     row['CHARGE'],           # price
                     row[description_key],      # description
                     hospital,   # hospital_id
                     result['filename'],
                     charge_type]            
            df.loc[idx,:] = entry


# Remove empty rows
df = df.dropna(how='all')

# Save data!
print(df.shape)
df.to_csv(output_data, sep='\t', index=False)
df.to_csv(output_year, sep='\t', index=False)
