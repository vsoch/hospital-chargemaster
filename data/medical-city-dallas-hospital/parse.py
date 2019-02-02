#!/usr/bin/env python

import os
from glob import glob
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

    print("Parsing %s" % filename)

    charge_type = 'standard'

    # service,price,hospital_stay_range\n'
    with open(filename, 'r') as filey:
        lines = filey.readlines()

    # They saved with comma as delimiter, but there are commas in description...
    # /facepalm
    # This data is not logically parseable.
    for l in range(1, len(lines)):
        line = lines[l].strip('\n').split(',')
        price_range = line[-3]
        description = ','.join(line[:-3])
        print(price_range)
        print(description)
        content = pandas.read_csv(filename)

# Remove empty rows
#df = df.dropna(how='all')

# Save data!
#print(df.shape)
#df.to_csv(output_data, sep='\t', index=False)
#df.to_csv(output_year, sep='\t', index=False)
