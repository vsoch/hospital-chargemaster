#!/usr/bin/env python

import os
import xmltodict
from glob import glob
import json
import datetime
import pandas

here = os.path.dirname(os.path.abspath(__file__))
folder = os.path.basename(here)
year = datetime.datetime.today().year
output_data = os.path.join(here, 'data-latest.tsv')
output_year = os.path.join(here, 'data-%s.tsv' % year)

latest = '%s/latest' % here

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

def process_workbook(content, df, hospital_id, filename, charge_type):    

    # First row is header
    sheets = content['Workbook']['Worksheet']
    if not isinstance(sheets, list):
        sheets = [content['Workbook']['Worksheet']]

    for sheet in sheets:
        for r in range(1, len(sheet['Table']['Row'])):
            idx = df.shape[0] + 1
            row = sheet['Table']['Row'][r]

            if charge_type == "drg":
                # <Cell><Data ss:Type="String">FINAL_DRG_NAME</Data></Cell>
                # <Cell><Data ss:Type="String">FINAL_DRG_CODE</Data></Cell>
                # <Cell><Data ss:Type="String">AVG_TOT_CHGS</Data></Cell>
 
                description = row['Cell'][0]['Data']['#text']
                code = row['Cell'][1]['Data']['#text']
                price = row['Cell'][1]['Data']['#text']
                items = [code, price, description, hospital_id, filename, charge_type]

            else:

                if "Data" not in row['Cell'][1]: 
                    continue 
                description = row['Cell'][0]['Data']['#text']            
                price = row['Cell'][1]['Data']['#text']
                items = [None, price, description, hospital_id, filename, charge_type]

                # <Cell ss:StyleID="s19"><Data ss:Type="String">MRH / JDCH</Data></Cell>
                # <Cell ss:StyleID="s19"/>
                # <Cell ss:StyleID="s19"><Data ss:Type="String">MRHS</Data></Cell>
                # <Cell ss:StyleID="s19"/>
                # <Cell ss:StyleID="s19"><Data ss:Type="String">MHW</Data></Cell>
                # <Cell ss:StyleID="s19"/>
                # <Cell ss:StyleID="s19"><Data ss:Type="String">MHP</Data></Cell>
                # <Cell ss:StyleID="s19"/>
                # <Cell ss:StyleID="s19"><Data ss:Type="String">MHM</Data></Cell>
            df.loc[idx, :] = items

    return df


for result in results:
    filename = os.path.join(latest, result['filename'])
    if not os.path.exists(filename):
        print('%s is not found in latest folder.' % filename)
        continue

    if os.stat(filename).st_size == 0:
        print('%s is empty, skipping.' % filename)
        continue

    if result['filename'] in seen:
        continue

    charge_type = "standard"
    if "drg" in filename.lower():
        charge_type = "drg"

    print('Parsing %s' % filename)

    # Option 1: parse an XML file
    if filename.endswith('xml'):
        with open(filename, 'r') as filey:
            content = xmltodict.parse(filey.read())

        df = process_workbook(content, df, 
                              result['uri'], 
                              result['filename'], 
                              charge_type)

# Remove empty rows
df = df.drop([1])
df = df.dropna(how='all')

# Save data!
print(df.shape)
df.to_csv(output_data, sep='\t', index=False)
df.to_csv(output_year, sep='\t', index=False)
