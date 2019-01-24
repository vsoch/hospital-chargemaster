#!/usr/bin/env python

import os
from glob import glob
import json
import pandas
import datetime

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

for result in results:
    filename = os.path.join(latest, result['filename'])
    if not os.path.exists(filename):
        print('%s is not found in latest folder.' % filename)
        continue

    if os.stat(filename).st_size == 0:
        print('%s is empty, skipping.' % filename)
        continue

    if result['filename'] in df.filename.tolist():
        continue

    print('Parsing %s' % filename)

    # Determine charge type - drg or standard
    if "drg" in filename:
        charge_type = "drg"
    else:
        charge_type = "standard"

    # We currently just have csv

    if filename.endswith('csv'):
        # DRG header: ['Facility', 'DRG', 'DRG Description', 'Average Covered Charges']
        if charge_type == "drg":
            content = pandas.read_csv(filename, skiprows=1)

        # Facility        CC               CC Description 1/1/19 Fee
        else:
            content = pandas.read_csv(filename)

    for row in content.iterrows():

        idx = df.shape[0] + 1
        if charge_type == "drg":
            df.loc[idx, 'hospital_id'] = row[1].Facility
            df.loc[idx, 'price'] = row[1]['Average Covered Charges']
            df.loc[idx, 'description'] = row[1]['DRG Description']
            df.loc[idx, 'charge_code'] = row[1]['DRG']

        else:
            # Find the fee column
            pricecol = [x for x in content.columns if "Fee" in x][0]
            df.loc[idx, 'hospital_id'] = row[1].Facility
            df.loc[idx, 'price'] = row[1][pricecol]
            df.loc[idx, 'description'] = row[1]['CC Description']
        df.loc[idx, 'charge_type'] = charge_type
        df.loc[idx, 'filename'] = result['filename']

    # Remove empty rows
    df = df.dropna(how='all')

    # Save data as we go
    print(df.shape)
    df.to_csv(output_data, sep='\t', index=False)
    df.to_csv(output_year, sep='\t', index=False)
