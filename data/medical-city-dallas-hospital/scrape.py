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

url ='https://medicalcityhospital.com/patient-financial/?page_name=pricing'

today = datetime.datetime.today().strftime('%Y-%m-%d')
outdir = os.path.join(here, today)
if not os.path.exists(outdir):
    os.mkdir(outdir)

from browser import ScraperRobot
driver = ScraperRobot()

# A list of lists, each is a row in one of two tables
entries = driver.get_download_urls(url)
filename =  os.path.basename('%s.csv' % hospital_id)
output_file = os.path.join(outdir, filename)

records = []
with open(output_file, 'w') as filey:
    for row in entries:
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
