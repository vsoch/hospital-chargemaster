#!/usr/bin/env python

import os
import requests
import json
import datetime
import shutil
import re
from bs4 import BeautifulSoup

here = os.path.dirname(os.path.abspath(__file__))
hospital_id = os.path.basename(here)

today = datetime.datetime.today()
year = int(today.year)

url ='https://cdn.iuhealth.org/resources/%s-Charge-CMS-Transparency.txt' % year

today = today.strftime('%Y-%m-%d')
outdir = os.path.join(here, today)
if not os.path.exists(outdir):
    os.mkdir(outdir)

# This url is a direct link to download, it looks like a tab separated file


filename = os.path.basename(url)
output_file = os.path.join(outdir, filename)
os.system('wget -O "%s" "%s"' % (output_file, url))
records = [ { 'hospital_id': hospital_id,
              'filename': filename,
              'date': today,
              'uri': filename,
              'name': filename,
              'url': url } ]

# Keep json record of all files included
records_file = os.path.join(outdir, 'records.json')
with open(records_file, 'w') as filey:
    filey.write(json.dumps(records, indent=4))

# This folder is also latest.
latest = os.path.join(here, 'latest')
if os.path.exists(latest):
    shutil.rmtree(latest)

shutil.copytree(outdir, latest)
