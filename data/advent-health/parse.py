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

columns = ['charge_code', 'price', 'description', 'hospital_id', 'filename']
df = pandas.DataFrame(columns=columns)

# Helper Functions - different formats of XML
def process_dataroot(content, df, filename):

    # Hospital name is the key that doesn't start with @
    for hospital_id in content['dataroot'].keys():
        if not hospital_id.startswith('@'):
            break

    for entry in content['dataroot'][hospital_id]:
        # ed means entry dict
        idx = df.shape[0] + 1
        ed = dict()
        for item, value in entry.items():
            if "code" in item.lower():
                ed['charge_code'] = value
            elif "description" in item.lower():
                ed['description'] = value
            elif "price" in item.lower():
                ed['price'] = value
        row = [ed['charge_code'], ed['price'], ed['description'], hospital_id, filename]
        df.loc[idx, :] = row

    return df


def process_workbook(content, df, hospital_id, filename):    
    # First row is header
    for r in  range(1, len(content['Workbook']['Worksheet']['Table']['Row'])):
        idx = df.shape[0] + 1
        description = row['Cell'][0]['Data']['#text']
        price = row['Cell'][1]['Data']['#text']
        items = [None, price, description, hospital_id, filename]
        df.loc[idx, :] = items
    return df


seen = []
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

    seen.append(result['filename'])
    print('Parsing %s' % filename)

    # Option 1: parse an XML file
    if filename.endswith('xml'):
        with open(filename, 'r') as filey:
            content = xmltodict.parse(filey.read())

        if "dataroot" in content:
            df = process_dataroot(content, df, filename)
        elif "Workbook" in content:
            df = process_workbook(content, df, result['uri'], result['filename'])

    # Save data as we go
    print(df.shape)
    df.to_csv(output_data, sep='\t', index=False)
    df.to_csv(output_year, sep='\t', index=False)
