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

url ='https://www.bjc.org/For-Patients-Billing-Visitors/Financial-Assistance-Resources/BJC-Hospital-Standard-Charges'

today = datetime.datetime.today().strftime('%Y-%m-%d')
outdir = os.path.join(here, today)
if not os.path.exists(outdir):
    os.mkdir(outdir)

from browser import ScraperRobot
driver = ScraperRobot()

download_url = driver.get_download_url(url)
filename =  os.path.basename(download_url.split('?')[0])  
filename = filename.replace('%20','-')

# We want to get the original file, not write a new one
output_file = os.path.join(outdir, filename)
os.system('wget -O "%s" "%s"' % (output_file, download_url))
records = [ { 'hospital_id': hospital_id,
              'filename': filename,
              'date': today,
              'uri': filename,
              'name': filename,
              'url': download_url }]


# Keep json record of all files included
records_file = os.path.join(outdir, 'records.json')
with open(records_file, 'w') as filey:
    filey.write(json.dumps(records, indent=4))

# This folder is also latest.
latest = os.path.join(here, 'latest')
if os.path.exists(latest):
    shutil.rmtree(latest)

shutil.copytree(outdir, latest)
