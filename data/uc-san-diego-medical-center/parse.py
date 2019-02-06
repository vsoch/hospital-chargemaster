#!/usr/bin/env python

import os
from glob import glob
import codecs
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
    if "diagnostic-related-group" in filename.lower():
        charge_type = "drg"

    print("Parsing %s" % filename)

    if filename.endswith('csv'):

        if charge_type == 'standard':
            #'Pharmacy code","Charge Code Description\n'
            with codecs.open(filename, "r", encoding='utf-8', errors='ignore') as filey:
                lines = filey.readlines()

            for l in range(7, len(lines)):
                idx = df.shape[0] + 1
                line = lines[l].strip('\n').strip('\r').strip().strip(',')

                # No idea why more than once price
                if line.count('$') > 1:
                    continue

                # Variable Pricing
                if '$' not in line:
                    continue
                description, price = line.split('$')
                price = price.replace(',','').replace('"','').strip()
                code, description = description.split(',', 1)
                entry = [code,                         # charge code
                         price,                        # price
                         description.strip(','),       # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         charge_type]            
                df.loc[idx,:] = entry

        # ['DRG_Definition', 'Average Charges']
        else:
            content = pandas.read_csv(filename)
            for row in content.iterrows():
                idx = df.shape[0] + 1
                code = row[1]['DRG_Definition'].split('-')[0]
                entry = [code,                         # charge code
                         row[1]['Average Charges'].replace('$','').replace(',','').strip(),  # price
                         row[1]['DRG_Definition'],        # description
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
