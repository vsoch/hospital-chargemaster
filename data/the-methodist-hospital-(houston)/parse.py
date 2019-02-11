#!/usr/bin/env python

import os
from glob import glob
import json
import codecs
import pandas
import datetime

# This data is also huge and we need to split into multiple files
here = os.path.dirname(os.path.abspath(__file__))
folder = os.path.basename(here)
latest = '%s/latest' % here
year = datetime.datetime.today().year

output_data = os.path.join(here, 'data-latest-1.tsv')
output_year = os.path.join(here, 'data-%s-1.tsv' % year)

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
seen = []

seen = ['pricing-transparency-faq.csv',
 'cdm-tmc.csv',
 'cdm-baytown.csv',
 'cdm-cl.csv',
 'cdm-sl.csv',
 'cdm-west.csv',
 'cdm-wb.csv']

for r in range(0, len(results)):
    result = results[r]
    filename = os.path.join(latest, result['filename'])
    if not os.path.exists(filename):
        print('%s is not found in latest folder.' % filename)
        continue

    if os.stat(filename).st_size == 0:
        print('%s is empty, skipping.' % filename)
        continue

    charge_type = 'standard'

    if result['filename'] in seen:
        continue
    seen.append(result['filename'])

    print("Parsing %s" % filename)

    if filename.endswith('csv'):

        if "transparency-faq" in filename:
            continue

        # 'Item,Charge Master Item Description,Price\r\n'
        with codecs.open(filename, "r", encoding='utf-8', errors='ignore') as filey:
            lines = filey.readlines()

        print(lines[0])
        for l in range(8279, len(lines)):
            idx = df.shape[0] + 1
            line = lines[l].strip('\n').strip('\r').strip().strip(',')
            if line == '':
                continue
            # There is a dollar amount with two...
            if line.count('$') > 1:
                pieces = line.split('$')
                description = pieces[0]
                price = ''.join(pieces[1:])                
            else:
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

    # When we hit 'cdm-hmtw.csv', save and refresh dataframe
    if result['filename'] == 'cdm-hmtw.csv':

        # Remove empty rows
        df = df.dropna(how='all')

        # Save data!
        print(df.shape)
        df.to_csv(output_data, sep='\t', index=False)
        df.to_csv(output_year, sep='\t', index=False)
        output_data = os.path.join(here, 'data-latest-2.tsv')
        output_year = os.path.join(here, 'data-%s-2.tsv' % year)
        df = pandas.DataFrame(columns=columns)
