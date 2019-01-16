#!/usr/bin/env python

# Simple script for extracting hospital names, urls, and identifiers.

import os
import pandas
import requests
from bs4 import BeautifulSoup

url ='https://qz.com/1518545/price-lists-for-the-115-biggest-us-hospitals-new-transparency-law/'
response = requests.get(url)
soup = BeautifulSoup(resyponse.text, 'lxml')
entries = soup.find_all("td")
df = pandas.DataFrame(columns = ["hospital_name", "hospital_id", "hospital_url"])

for entry in entries:
    hospital_id = entry.text.strip().lower().replace(' ','-')
    hospital_url = entry.find('a', href=True)['href']
    hospital_name = entry.text.strip()
    df.loc[hospital_id] = [hospital_name, hospital_id, hospital_url]

# Save the data frame to file
df.to_csv("hospitals.tsv", sep="\t", index=False)

# Create a data folder
if not os.path.exists('data'):
    os.mkdir('data')

# Create a subfolder for each
for hospital in df.hospital_id:
    if not os.path.exists('data/%s' % hospital):
        os.mkdir('data/%s' % hospital)
