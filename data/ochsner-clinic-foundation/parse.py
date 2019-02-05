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

seen = []

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

    if result['filename'] in seen:
        print('Already parsed %s' %filename)
        continue

    print("Parsing %s" % filename)
    seen.append(result['filename'])

    if filename.endswith('csv'):

        content = pandas.read_csv(filename)
        # Columns are either "Item" and "Amount" or
        #                    "Description" and "Amount"
        # One file has an extra third column.
        columns = content.columns.tolist()
        columns[0] = "Description"
        columns[1] = "Amount"

        if len(columns) == 3:
            # There is a bug that values spread over two columns
            columns[2] = "Amount1"
        content.columns = columns

        for row in content.iterrows():
            idx = df.shape[0] + 1
            price = row[1]['Amount']
            
            # If price is null, check the other price column
            if pandas.isnull(price) and "Amount1" in content.columns.tolist():
                price = row[1]['Amount']
 
            # Skip if it's still null
            if pandas.isnull(price):
                continue

            price = price.replace('$','').replace(',','').strip()
            entry = [None,                         # charge code
                     price,             # price
                     row[1]['Description'],        # description
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
