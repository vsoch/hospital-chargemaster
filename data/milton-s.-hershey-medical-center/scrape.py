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

here = os.path.dirname(os.path.abspath(__file__))
hospital_id = os.path.basename(here)

url = 'https://hmc.pennstatehealth.org/patients-families-and-visitors/billing-and-medical-records/request-a-price-estimate'

today = datetime.datetime.today().strftime('%Y-%m-%d')
outdir = os.path.join(here, today)
if not os.path.exists(outdir):
    os.mkdir(outdir)

# The link we want is to a file on box
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

from browser import ScraperRobot
driver = ScraperRobot()

rows = driver.get_rows(url)

records = []

filename =  os.path.basename('%s.csv' % hospital_id)
output_file = os.path.join(outdir, filename)
with open(output_file, 'w') as filey:
    filey.writelines('description,charge_amount\n')
    for row in rows:
        filey.writelines(','.join(row) + '\n')
    record = { 'hospital_id': hospital_id,
               'filename': filename,
               'date': today,
               'uri': filename,
               'name': filename,
               'url': url }

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
