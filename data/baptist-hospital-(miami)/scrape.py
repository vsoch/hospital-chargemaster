#!/usr/bin/env python

import os
import requests
import json
import datetime
import shutil
from bs4 import BeautifulSoup

# The drivers must be on path
drivers = os.path.abspath('../../drivers')
os.environ['PATH'] = "%s:%s" %(drivers, os.environ['PATH'])

from browser import ScraperRobot
driver = ScraperRobot()

here = os.path.dirname(os.path.abspath(__file__))
hospital_id = os.path.basename(here)

url = 'https://baptisthealth.net/en/facilities/baptist-hospital-miami/pages/pricing-information.aspx'

driver.download(url)


today = datetime.datetime.today().strftime('%Y-%m-%d')
outdir = os.path.join(here, today)
if not os.path.exists(outdir):
    os.mkdir(outdir)

# Each folder will have a list of records
records = []

for entry in soup.find_all('a', href=True):
    entry_url = entry['href']
    if "hospitalpriceindex.com" in entry_url:
        print(entry_url)

        # Need to scrape this live
        rows = driver.download(entry_url)
        entry_name = entry.text
        entry_uri = entry_name.strip().replace(' ','-')
        filename =  os.path.basename('%s.csv' % entry_uri)  

        # We want to get the original file, not write a new one
        output_file = os.path.join(outdir, filename)
        with open(output_file, 'w') as filey:
            filey.writelines('charge_code,description,charge_amount\n')
            for row in rows:
                filey.writelines(','.join(row))

        record = { 'hospital_id': hospital_id,
                   'filename': filename,
                   'date': today,
                   'uri': entry_uri,
                   'name': entry_name,
                   'url': entry_url }

        records.append(record)

# Keep json record of all files included
records_file = os.path.join(outdir, 'records.json')
with open(records_file, 'w') as filey:
    filey.write(json.dumps(records, indent=4))

# This folder is also latest.
latest = os.path.join(here, 'latest')
if os.path.exists(latest):
    shutil.rmtree(latest)

shutil.copytree(outdir, latest)
