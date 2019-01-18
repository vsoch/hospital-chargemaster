#!/usr/bin/env python

import os
import requests
import json
import datetime
import shutil
from bs4 import BeautifulSoup

here = os.path.dirname(os.path.abspath(__file__))
hospital_id = os.path.basename(here)

url ='https://www.orlandohealth.com/patients-and-visitors/patient-financial-resources/pricing-transparency-guide'

today = datetime.datetime.today().strftime('%Y-%m-%d')
outdir = os.path.join(here, today)
if not os.path.exists(outdir):
    os.mkdir(outdir)

prefix = "https://www.dukehealth.org"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

records = []
rows = []

for row in soup.find_all('tr'):
    cols = row.find_all('td')
    values = [c.text for c in cols]
    if len(values) != 2:
        break
    rows.append(values)
 
filename =  os.path.basename('%s.csv' % hospital_id)
output_file = os.path.join(outdir, filename)
with open(output_file, 'w') as filey:
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
