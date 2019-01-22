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

columns = ['charge_code', 'price', 'description', 'hospital_id', 'filename']
df = pandas.DataFrame(columns=columns)

for result in results:
    filename = os.path.join(latest, result['filename'])
    if not os.path.exists(filename):
        print('%s is not found in latest folder.' % filename)
        continue

    if os.stat(filename).st_size == 0:
        print('%s is empty, skipping.' % filename)
        continue

    print('Parsing %s' % filename)

    # We currently just have csv
    if filename.endswith('csv'):
        content = pandas.read_csv(filename)

    # The csv columns are DESCRIPTION and CHARGE
    df.loc[:, 'price'] = content['CHARGE']
    df.loc[:, 'description'] = content['DESCRIPTION']

    # Remove empty rows
    df = df.dropna(how='all')

    # Save data as we go
    print(df.shape)
    df.to_csv(output_data, sep='\t', index=False)
    df.to_csv(output_year, sep='\t', index=False)
