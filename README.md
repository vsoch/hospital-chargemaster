# Hospital Chargemaster

This is the hospital chargemaster [Dinosaur Dataset](https://vsoch.github.io/datasets)

<a target="_blank" href="https://camo.githubusercontent.com/d0eb19f161d4795a9c137b9b71c70b008d7c5e8e/68747470733a2f2f76736f63682e6769746875622e696f2f64617461736574732f6173736574732f696d672f61766f6361646f2e706e67"><img src="https://camo.githubusercontent.com/d0eb19f161d4795a9c137b9b71c70b008d7c5e8e/68747470733a2f2f76736f63682e6769746875622e696f2f64617461736574732f6173736574732f696d672f61766f6361646f2e706e67" alt="https://vsoch.github.io/datasets/assets/img/avocado.png" data-canonical-src="https://vsoch.github.io/datasets/assets/img/avocado.png" style="max-width:100%; float:right" width="100px"></a>

## What is this data?

As of January 1, 2019, hospitals are required to share their price lists. However,
 it remains a problem that the data released
[is not intended for human consumption](https://qz.com/1518545/price-lists-for-the-115-biggest-us-hospitals-new-transparency-law/). To make the data more readily available, in a single place, and checked monthly for updates, I've created
this repository.

## How does it work?

### 1. Get List of Hospital Pages

We have compiled a list of hospitals and links in the [hospitals.tsv](hospitals.tsv) 
file, generated via the [0.get_hospitals.py](0.get_hospitals.py) script. 
The file includes the following variables, separated by tabs::

 - **hospital_name** is the human friendly name
 - **hospital_url** is the human friendly URL, typically the page that includes a link to the data.
 - **hospital_uri** is the unique identifier for the hospital, the hospital name, in lowercase, with spaces replaced with `-`

This represents the original set of hospitals that I obtained from a [compiled list](https://www.cms.gov/newsroom/fact-sheets/fiscal-year-fy-2019-medicare-hospital-inpatient-prospective-payment-system-ipps-and-long-term-acute-0), and is kept
for the purpose of keeping the record.

### 2. Organize Data

Each hospital has records kept in a subfolder in the [data](data) folder. Specifically,
each subfolder is named according to the hospital name (made all lowercase, with spaces 
replaced with `-`). If a subfolder begins with an underscore, it means that I wasn't
able to find the charge list on the hospital site (and maybe you can help?) 
Within that folder, you will find:

 - `scrape.py`: A script to scrape the data
 - `browser.py`: If we need to interact with a browser, we use selenium to do this.
 - `latest`: a folder with the last scraped (latest data files)
 - `YYYY-MM-DD` folders, where each folder includes:
   - `records.json` the complete list of records scraped for a particular data
   - `*.csv` or `*.xlsx` or `*.json`: the scraped data files.

The first iteration was run locally (to test the scraping). One significantly different
scraper is the [oshpd-ca](data/oshpd-ca) folder, which includes over 795 hospitals! Way to go
California! Additionlly, [avent-health](data/advent-health) provides (xml) charge lists
for a ton of states.

#### Why do you have some redundant code?

It is the case that the code in the scrape.py files (and browser.py) is redundant. We do this so
that each folder is a modular solution to retrieve the data. If you are interested in just
one hospital, you can use the folder on its own. The one exception is with the browser (Chrome)
driver that is shared in the [drivers](drivers) folder at the root of the repository.

### 3. Automation

In order to make this automated, we will do the following:

 1. Set the repository up with continuous integration, scheduled to run once a month
 2. We test that each hospital (subfolder in data) is added to hospitals.tsv, is named correctly, and has a script to scrape.
 3. We are flexible with allowing each page to have differently named files, however if there is an error with obtaining the files, we are alerted (and tests fail)

**also under development**

## How do I contribute?

The original dataset was obtained from an article that [listed the top 115 US Hospitals](https://www.cms.gov/newsroom/fact-sheets/fiscal-year-fy-2019-medicare-hospital-inpatient-prospective-payment-system-ipps-and-long-term-acute-0), but this isn't to say that other hospitals aren't
important and deserving to belong here! If you want to add a hospital:

 1. Add your hospital name, identifier, and (human friendly) link to the [hospitals.tsv](hospitals.tsv) file. If you add a hospital folder and fail to update this file, or update the file and forget or misname the folder an error will be triggered.
 2. Create a subfolder based on the `hospital_uri` from the file.
 3. Write a `scrape.py` script in the folder. You can use others as templates, but the file should generate an output directory with the present date, and recursive copy the new folder to be latest.

The data will be updated monthly, or when a pull request is issued to update the repository.
Upon merge, the generated latest data will be pushed back to the repository.
