#!/usr/bin/env python

import os
import re
from glob import glob
import json
import pandas
import datetime
import codecs

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

    if result['filename'] in seen:
        continue
    seen.append(result['filename'])

    print("Parsing %s" % filename)

    if filename.endswith('csv'):

        if "uncmc-published" in filename or "rex-published" in filename or "wayne-published" in filename:

            # 'Charge Description,Receivable Owner,Service ID,Service Provider,Service Type,Eff Rate Amt\r\n'
            with codecs.open(filename, "r", encoding='utf-8', errors='ignore') as filey:
                lines = filey.readlines()

            for l in range(2, len(lines)):
                idx = df.shape[0] + 1
                line = lines[l].strip('\n').strip('\r').strip(',').strip()
                price = line.split(',')[-1]
                line = line.replace(',%s' %price, '')
                parts = re.split(r',(?=")', line)   
                description = parts[0].strip('"')
                price = price.strip('"').replace('$','').replace(',','').strip()
                if len(parts) > 1:
                    code = parts[1].strip('"').strip()
                else:
                    code = None
                entry = [code,                         # charge code
                         price,                        # price
                         description,                  # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         charge_type]            
                df.loc[idx,:] = entry

        # ['DESCRIPTION', 'CHARGE', 'CPT CODE']
        elif charge_type == "standard":

            if 'caldwell' in filename or "chatham" in filename or "johnston" in filename or "lenoir" in filename.lower() or "nash" in filename or "pardee" in filename:
                content = pandas.read_csv(filename, header=None)
                content.columns = ['DESCRIPTION', 'CPT CODE', 'CHARGE']
                print(content.head())
            else:
                content = pandas.read_csv(filename)

            columns = [x.strip() for x in content.columns.tolist()]
            content.columns = columns
            for row in content.iterrows():
                idx = df.shape[0] + 1
                price = row[1]['CHARGE']
                if not isinstance(price, float):
                    price = price.replace('$','').replace(',','').strip()
                entry = [row[1]['CPT CODE'],           # charge code
                         price,             # price
                         row[1]['DESCRIPTION'],        # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         charge_type]            
                df.loc[idx,:] = entry

        else:

            # ['Location', 'MS DRG - Code', 'MS DRG - Description',' Average Charge ']
            if "csv-caldwell" in filename or "csv-chatham" in filename or "johnston-drg" in filename or "pardee-drg" in filename or "unc-hospitals-drg" in filename or "rex-drg" in filename:
                content = pandas.read_csv(filename, skiprows=5)
                code_key = "MS DRG - Code"
                description_key = 'MS DRG - Description'
                price_key = ' Average Charge '

            # ['MS-DRG ', 'MS-DRG Title', 'AVERAGE CHARGES'
            elif "lenoir-drg" in filename:
                content = pandas.read_csv(filename)
                code_key = "MS-DRG "
                description_key = 'MS-DRG Title'
                price_key = 'AVERAGE CHARGES'

            # ['DRG', 'DRG Description', '   Charges', 'DRG Payment', ' Prim Carrier', ' Prim Plan', 'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8', 'DRG.1', 'DESC', 'AVG CHRG ', ' ']
            elif "nash-drg" in filename:
                content = pandas.read_csv(filename)
                code_key = "DRG"
                description_key = 'DRG Description'
                price_key = 'AVG CHRG '

            # ['DRG', 'DESCRIPTION', 'AVG CHARGES']
            elif "rockingham-drg" in filename:
                content = pandas.read_csv(filename)
                code_key = "DRG"
                description_key = 'DESCRIPTION'
                price_key = 'AVG CHARGES'

            # (['MSDRG', 'MSDRG Desc', 'Avg Charge', 'Unnamed: 3', 'Unnamed: 4']
            else: # csv-wayne
                content = pandas.read_csv(filename, skiprows=1)
                code_key = "MSDRG"
                description_key = 'MSDRG Desc'
                price_key = 'Avg Charge'

            for row in content.iterrows():
                price = row[1][price_key]
                if pandas.isnull(price):
                    continue
                if not isinstance(price, float):
                    price = price.replace('$','').replace(',','').strip()
                entry = [row[1][code_key],             # charge code
                         price,  # price
                         row[1][description_key],      # description
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
