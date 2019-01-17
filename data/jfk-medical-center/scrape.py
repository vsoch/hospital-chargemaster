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

url ='https://jfkmc.com/about/legal/detail-price-list.dot'

today = datetime.datetime.today().strftime('%Y-%m-%d')
outdir = os.path.join(here, today)
if not os.path.exists(outdir):
    os.mkdir(outdir)

from browser import ScraperRobot
driver = ScraperRobot()

links = driver.get_download_urls(url)

records = []
for download_url in links:
    filename =  os.path.basename(download_url.split('?')[0])  
    output_file = os.path.join(outdir, filename)
    os.system('wget -O "%s" "%s"' % (output_file, download_url))
    record = { 'hospital_id': hospital_id,
               'filename': filename,
               'date': today,
               'uri': filename,
               'name': filename,
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
