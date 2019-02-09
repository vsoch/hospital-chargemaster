#!/usr/bin/env python

import os
from glob import glob
import json
import pandas
from statistics import mean
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
    if 'supply' in result['filename'].lower():
        charge_type = 'supply'
    if 'pharmacy' in result['filename'].lower():
        charge_type = 'pharmacy'

    
    if result['filename'] in seen:
        continue

    seen.append(result['filename'])
    
    print("Parsing %s" % filename)

    if filename.endswith('csv'):

       # ['List ID', 'CPT Code', 'Procedure Description', 'Unit Charge', 'Unnamed: 4'],
        if "professional" in filename.lower():
            content = pandas.read_csv(filename, skiprows=3)
            description_key = 'Procedure Description'
            price_key = 'Unit Charge'
            code_key = 'CPT Code'

        # ['List ID', 'IP/OP', 'Revenue Code', 'Revenue Code Description', 'Average Charges per Date of Service']
        elif charge_type == 'pharmacy':
            content = pandas.read_csv(filename, skiprows=3)
            description_key = 'Revenue Code Description'
            price_key = 'Average Charges per Date of Service'
            code_key = 'Revenue Code'

        # 'List ID', 'CPT Code', 'Supply Category', 'Description', 'Unit Charge']
        elif charge_type == 'supply':
            content = pandas.read_csv(filename, skiprows=4)
            description_key = 'Description'
            price_key = 'Unit Charge'
            code_key = 'CPT Code'

        # ['List ID', 'Revenue Code Description', 'CPT Code', 'Procedure Name','Unit Charge']
        elif charge_type == 'standard':
            content = pandas.read_csv(filename, skiprows=3)
            description_key = 'Revenue Code Description'
            price_key = 'Unit Charge'
            code_key = 'CPT Code'

        for row in content.iterrows():
            idx = df.shape[0] + 1
            price = row[1][price_key]
            if not isinstance(price, float):
                if price.count('$') > 1:
                    prices = [x.replace('$','').replace(',','') for x in price.split('-')]
                    price = mean([float(x) for x in prices])
                else:
                    price = price.replace('$','').replace(',','').strip()
            code = row[1][code_key]
            if code == "BLANK":
                code = None
            entry = [code,                         # charge code
                     price,             # price
                     row[1][description_key],        # description
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
