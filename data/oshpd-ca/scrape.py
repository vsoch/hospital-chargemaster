#!/usr/bin/env python

import os
import requests
import json
import datetime
import shutil
import re
from bs4 import BeautifulSoup

here = os.path.dirname(os.path.abspath(__file__))

today = datetime.datetime.today()
year = int(today.year) - 1

url ='https://oshpd.ca.gov/data-and-reports/cost-transparency/hospital-chargemasters/%s-chargemasters/' % year

today = today.strftime('%Y-%m-%d')
outdir = os.path.join(here, today)
if not os.path.exists(outdir):
    os.mkdir(outdir)

response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

# Each folder will have a list of records
records = []

entries = soup.find_all('td')[1:]
prefix = "https://oshpd.ca.gov"

while len(entries) > 0:
    entry_name = entries.pop(0).text

    # Skip first column
    if entry_name == str(year):
        continue

    entry_url = entries.pop(0)
    entry_a = entry_url.find('a') 
    hospital_id = entry_name.strip().lower().replace(' ','-')
    download_url = prefix + entry_a['href']
    filename = download_url.split('\\')[-1] 
    output_file = os.path.join(outdir, filename)
    os.system('wget -O "%s" "%s"' % (output_file, download_url))
    record = { 'hospital_id': hospital_id,
               'filename': filename,
               'date': today,
               'uri': hospital_id,
               'name': entry_name,
               'url': download_url }

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
