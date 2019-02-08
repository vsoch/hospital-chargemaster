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

    if filename.endswith('csv'):

        if re.search('(shelby|mansfield)', filename.lower()):
            continue

            with codecs.open(filename, "r", encoding='utf-8', errors='ignore') as filey:
                lines = filey.readlines()

            # 'SERVICE CATEGORY,DESCRIPTION,CHARGE,DOSE,STATE OF OHIO REQUIREMENT\r\n'
            for l in range(2,len(lines)):
                line = lines[l].strip('\n').strip('\r')
                idx = df.shape[0] + 1
                description =  line.split(',')[1].strip()
                price = line.split(',')[-3].replace('$','').replace(',','').strip()
                entry = [None,                         # charge code
                         price,             # price
                         description,        # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         charge_type]            
                df.loc[idx,:] = entry

        elif charge_type == "standard":

            if "doctors-dublin-grant-grovecity-riverside" in filename:
                content = pandas.read_csv(filename, skiprows=1)

            else:
                content = pandas.read_csv(filename, low_memory=False)
                
            for row in content.iterrows():
                idx = df.shape[0] + 1
                entry = [None,                         # charge code
                         row[1]['CHARGE'],             # price
                         row[1]['DESCRIPTION'],        # description
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
