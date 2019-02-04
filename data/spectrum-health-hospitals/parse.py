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
    if "drg" in filename.lower():
        charge_type = "drg"

    print("Parsing %s" % filename)

    # 'Unnamed: 0', 'DRG', 'MS-DRG Name', ' Grand Rapids ', ' Regional * ', 'Unnamed: 5']
    if filename.endswith('csv'):

        if charge_type == "drg":
            content = pandas.read_csv(filename)
            description_key = 'DRG Desc'
            price_key = "Avg Charge"
            code_key = 'DRG#'

            if ' Grand Rapids ' in content.columns.tolist():
                price_key = ' Grand Rapids '    
                code_key = "DRG"
                description_key = 'MS-DRG Name'         

            for row in content.iterrows():
                idx = df.shape[0] + 1
                price = row[1][price_key]
                if pandas.isnull(price):
                    price = row[1][' Regional * ']
                if pandas.isnull(price):
                    continue           
                entry = [row[1][code_key],             # charge code
                         price.replace('$','').replace(',','').strip(),            # price
                         row[1][description_key],      # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         charge_type]            
                df.loc[idx,:] = entry

        else:

            with codecs.open(filename, "r", encoding='utf-8', errors='ignore') as filey:
                lines = filey.readlines()
 
            # ',CODE,NAME,LAKELAND,LAKELAND INPATIENT LABS,LAKELAND OUTPATIENT LABS,LAKELAND BLOOD BANK,LAKELAND REFERENCE LAB,LAKELAND RESPIRATORY THERAPY LAB,WATERVLIET,WATERVLIET INPATIENT LABS,WATERVLIET OUTPATIENT LABS,WATERVLIET BLOOD BANK\r\n'
            if "lakeland" in filename.lower():
                for l in range(1, len(lines)):
                    idx = df.shape[0] + 1
                    line = lines[l].strip('\n').strip('\r')
                    price = line.split(',')[-4].replace('$','').replace(',','').strip()
                    description = line.split(',')[2]
                    code = line.split(',')[1]
                    entry = [code,               # charge code
                             price,              # price
                             description,        # description
                             result["hospital_id"],        # hospital_id
                             result['filename'],
                             charge_type]            
                    df.loc[idx,:] = entry

            # ",PROCEDURE CODE,PROCEDURE DESCRIPTION, CHILDREN'S HOSPITAL , BUTTERWORTH , BLODGETT , GRAND RAPIDS OFF-CAMPUS , REGIONAL ** , REFERENCE LABS ,,\r\n"
            else:
                for l in range(4, len(lines)):
                    idx = df.shape[0] + 1
                    line = lines[l].strip('\n').strip('\r')
                    price = line.split(',')[4].replace('$','').replace(',','').strip()
                    if price == "":
                        continue
                    description = line.split(',')[2]
                    code = line.split(',')[1]
                    entry = [code,               # charge code
                             price,              # price
                             description,        # description
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
