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
    if "drg" in filename.lower():
        charge_type = "drg"

    print("Parsing %s" % filename)

    if filename.endswith('txt'):

        with codecs.open(filename, "r", encoding='utf-8', errors='ignore') as filey:
            lines = filey.readlines()

        if charge_type == "standard":

            # Charge Description,Receivable Owner,Service ID,Service Provider,Service Type,Eff Rate Amt
            for l in range(1, len(lines)):
                idx = df.shape[0] + 1
                line = lines[l].strip('\n').strip('\r')
                code = re.search('[0-9]{8}',line)
                if code == None:
                    code = re.search(',([0-9]+),',line)
                if code != None:
                    code = code.group().strip(',')
                    description = ' '.join(line.split(',')[4])
                else:
                    description = line.split(',')[:4]
                price = line.split(',')[-1].replace(',','').replace('"','')
                if pandas.isnull(price) or price in ['', None]:
                    continue
                entry = [code,                         # charge code
                         price,                        # price
                         description,                  # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         charge_type]            
                df.loc[idx,:] = entry

        elif charge_type == "drg":

            # 'Enc - MS DRG,Enc - MS DRG Desc,Sum of Average Charge\r\n'
            for l in range(1, len(lines)):
                idx = df.shape[0] + 1
                line = lines[l].strip('\n').strip('\r')
                code = line.split(',')[0].strip()
                description = line.split(',')[1:-1]
                description = ','.join(description).replace('"','')
                price = line.split(',')[-1].replace(',','')
                if pandas.isnull(price) or price in ['', None]:
                    continue
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
