#!/usr/bin/env python

import os
from glob import glob
import re
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

seen = []
for result in results:
    filename = os.path.join(latest, result['filename'])
    if not os.path.exists(filename):
        print('%s is not found in latest folder.' % filename)
        continue

    if os.stat(filename).st_size == 0:
        print('%s is empty, skipping.' % filename)
        continue

    charge_type = 'standard'
    if "drg" in filename.lower():
        charge_type = "drg"

    print("Parsing %s" % filename)
 
    if result['filename'] in seen:
        continue
    seen.append(result['filename'])

    if filename.endswith('txt'):

        if charge_type == "standard":

            # 'Charge Description,Receivable Owner,Service ID,Service Provider,Service Type,Eff Rate Amt\r\n'
            with codecs.open(filename, "r", encoding='utf-8', errors='ignore') as filey:
                lines = filey.readlines()

            for l in range(13355, len(lines)):
                idx = df.shape[0] + 1
                line = lines[l].strip('\n').strip('\r').strip(',').strip()
                if line == '':
                    continue
                parts = re.split(r',(?=")', line)
                if len(parts) == 1:
                    parts = parts[0].split(',')
                    price = parts[-1]
                else:
                    price = parts[-1]
                    parts = parts[0].split(',')

                if len(parts) == 1:
                    continue

                description = parts[0]
                code = parts[2]                    
                price = price.strip('"').replace(',','')
                entry = [code,                         # charge code
                         price,                        # price
                         description,                  # description
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
