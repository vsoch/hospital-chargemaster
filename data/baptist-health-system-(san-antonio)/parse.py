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

def process_drg(content, result, df):
    '''the drg flie is a matrix of hospitals (columns) by price, needs
       different processing
    '''
    for row in content.iterrows():
        hospitals = [x for x in row[1].index.tolist() if "DRG" not in x]
        prices = [x for x in row[1].tolist() if not isinstance(x,str)]
        charge_code = row[1]['DRG Code'].split('-')[0].strip()
        for i in range(len(prices)):
            price = prices[i]
            hospital = hospitals[i]
            idx = df.shape[0] + 1
    
            entry = [charge_code,                 # charge code
                     price,                # price
                     row[1]['DRG Code'],   # description
                     hospital,             # hospital_id
                     result['filename'],
                     "drg"]
        df.loc[idx,:] = entry
    return df

# First parse standard charges (doesn't have DRG header)
for result in results:
    filename = os.path.join(latest, result['filename'])
    if not os.path.exists(filename):
        print('%s is not found in latest folder.' % filename)
        continue

    if os.stat(filename).st_size == 0:
        print('%s is empty, skipping.' % filename)
        continue

    if filename.endswith('xlsx'):
        content = pandas.read_excel(filename)

    # We need to combine Facility, DRG, 
    print("Parsing %s" % filename)
 
    # Single DRG file is processed differently
    if 'DRG Code' in content.columns:
        df = process_drg(content, result, df)
        continue

    # Update by row
    # ['CDM NAME', 'HOSPITAL', 'TECHNICAL DESCRIPTION', 'TOTAL CHARGE']
    for row in content.iterrows():
        idx = df.shape[0] + 1
        entry = [None,                              # charge code
                 row[1]["TOTAL CHARGE"],            # price
                 row[1]["TECHNICAL DESCRIPTION"],   # description
                 row[1].HOSPITAL,                   # hospital_id
                 result['filename'],
                 'standard']                        # filename
        df.loc[idx,:] = entry

# Remove empty rows
df = df.dropna(how='all')

# Save data!
print(df.shape)
df.to_csv(output_data, sep='\t', index=False)
df.to_csv(output_year, sep='\t', index=False)
