#!/usr/bin/env python

import os
import requests
import json
import datetime
import shutil
from bs4 import BeautifulSoup

here = os.path.dirname(os.path.abspath(__file__))
hospital_id = os.path.basename(here)

url ='https://www.aurorahealthcare.org/patients-visitors/billing-payment/health-care-costs'
prefix = "https://www.aurorahealthcare.org"

today = datetime.datetime.today().strftime('%Y-%m-%d')
outdir = os.path.join(here, today)
if not os.path.exists(outdir):
    os.mkdir(outdir)

response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')
entries = soup.find("div", {"id":"Auroras-Standard-Charges"}).find_all('a')

# Each folder will have a list of records
records = []

for entry in entries:
    entry_name = entry.text.strip()
    entry_uri = entry_name.lower().replace(' ','-')
    hospital_url = prefix + entry['href']
    response = requests.get(hospital_url)

    # We want to get the original file, not write a new one
    filename =  os.path.basename(hospital_url.split('?')[0])    
    output_file = os.path.join(outdir, filename)
    os.system('wget -O %s %s' % (output_file, hospital_url))

    record = { 'hospital_id': hospital_id,
               'filename': filename,
               'date': today,
               'uri': entry_uri,
               'name': entry_name,
               'url': hospital_url }
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
