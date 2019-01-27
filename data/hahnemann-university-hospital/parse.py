#!/usr/bin/env python

import os
from glob import glob
import json
import pandas
import codecs
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

    if filename.endswith('xlsx'):

        # ['FAC', 'DEPT', 'TECHNICAL DESCRIPTION', 'BILLING DESCRIPTION', 'CC',
        # 'IPREV', 'OPREV', 'A9', 'A10', 'HCPCS', 'MOD', 'GOV'T*nb', 'MCR*nc',
        # 'TOTAL CHARGE', 'STATUS', 'PF', 'SLH UNIT', 'MCR*sa', 'PASSTHRU',
        # 'PARTB only', 'PROFESSIONAL FEE', 'PRO CO TYPE', 'MACS EXCL', 'GL FLAG',
        # 'DEPT TYPE', 'LAST MAINTENANCE DATE', 'DATA ACCESS', 'SURG MIN',
        # 'STAT FLAG 03', 'STAT FLAG 04', 'STAT FLAG 05', 'MULTIPLIER 03',
        # 'MULTIPLIER 04', 'MULTIPLIER 05', 'Flags', 'IP Qty', 'IP TTL Rev',
        # 'OP Qty', 'OP TTL Rev', 'Total Qty', 'Total Revenue',
        # 'HOSPITAL CHARGE']
        content = pandas.read_excel(filename, sheet_name=1, skiprows=8)
        content = content.dropna(how='all')

        for row in content.iterrows():
            idx = df.shape[0] + 1
            price = row[1]['HOSPITAL CHARGE']
            if pandas.isnull(price):
                continue
            entry = [row[1]['CC'],                 # charge code
                     price,                        # price
                     row[1]['TECHNICAL DESCRIPTION'],    # description
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
