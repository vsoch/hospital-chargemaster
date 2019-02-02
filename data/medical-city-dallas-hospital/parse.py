#!/usr/bin/env python

import os
from glob import glob
from statistics import mean 
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
        rows = filey.readlines()


    # They saved with comma as delimiter, but there are commas in description...
    # /facepalm

    # The first is the header column
    for row in rows[1:]:
        comma_split = row.split(",")

        # We don't use this
        hospital_stay_range = comma_split[-1]  ## assume no commas in last argument
        with_dollars = [i for i, piece in enumerate(comma_split) if "$" in piece]
    
        # Case 1: no price found
        if len(with_dollars) == 0:

            ## assume price is second-to-last entry
            price = comma_split[-2]

            ## assume service is everything before first two commas
            service = "".join(comma_split[:-2])

        elif len(with_dollars) == 1 or len(with_dollars) == 2:
            first_dollar = min(with_dollars)
            price = "".join(comma_split[first_dollar: -1])
            service = "".join(comma_split[:first_dollar])

        else:
            # more than two dollar signs found in one entry
            continue
 
        # No price given.
        if "N/A" in price:
            continue

        # If the price is a range, take average
        price = price.replace('$','')
        if "-" in price:
            prices = [float(x.strip()) for x in price.split('-')]
            price = mean(prices)
        else:
            price = float(price)
   
        idx = df.shape[0] + 1
        entry = [None,                     # charge code
                 price,                    # price
                 service,              # description
                 result["hospital_id"],    # hospital_id
                 result['filename'],
                 charge_type]            
        df.loc[idx,:] = entry

# Remove empty rows
df = df.dropna(how='all')

# Save data!
print(df.shape)
df.to_csv(output_data, sep='\t', index=False)
df.to_csv(output_year, sep='\t', index=False)
