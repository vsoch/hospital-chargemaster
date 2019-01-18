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

url ='https://www.atlantichealth.org/patients-visitors/insurance/out-network-insurance.html'
prefix = "https://www.atlantichealth.org/"

today = datetime.datetime.today().strftime('%Y-%m-%d')
outdir = os.path.join(here, today)
if not os.path.exists(outdir):
    os.mkdir(outdir)

response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

for entry in soup.find_all('a', href=True):
    download_url = prefix + entry['href']
    if '.xls' in download_url:  
        break

filename =  os.path.basename(download_url.split('?')[0])  
filename = filename.replace('%20','-')
output_file = os.path.join(outdir, filename)

# The regular wget will be blocked, make a new one :)
previous_location = os.getcwd()
os.chdir(here)
os.system('/bin/bash wget.sh %s %s' % (download_url, output_file))

records = [{ 'hospital_id': hospital_id,
             'filename': filename,
             'date': today,
             'uri': filename,
             'name': filename,
             'url': download_url } ]

os.chdir(previous_location)

# Keep json record of all files included
records_file = os.path.join(outdir, 'records.json')
with open(records_file, 'w') as filey:
    filey.write(json.dumps(records, indent=4))

# This folder is also latest.
latest = os.path.join(here, 'latest')
if os.path.exists(latest):
    shutil.rmtree(latest)

shutil.copytree(outdir, latest)
