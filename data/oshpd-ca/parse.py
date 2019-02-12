#!/usr/bin/env python

import os
from glob import glob
import json
import pandas
import datetime

# This is a challenging dataset because it's so big!
# We will do our best to break the data into pieces

here = os.path.dirname(os.path.abspath(__file__))
folder = os.path.basename(here)
latest = '%s/latest' % here
year = datetime.datetime.today().year

output_data = os.path.join(here, 'data-latest-1.tsv')
output_year = os.path.join(here, 'data-%s-1.tsv' % year)

# Don't continue if we don't have latest folder
if not os.path.exists(latest):
    print('%s does not have parsed data.' % folder)
    sys.exit(0)

# Don't continue if we don't have results.json
results_json = os.path.join(latest, 'records.json')
if not os.path.exists(results_json):
    print('%s does not have results.json' % folder)
    sys.exit(1)

with open(results_json, 'r') as filey:
    results = json.loads(filey.read())

columns = ['charge_code', 
           'price', 
           'description', 
           'hospital_id', 
           'filename', 
           'charge_type']

df = pandas.DataFrame(columns=columns)

seen = []
for r in range(423 ,len(results)):
    result = results[r]
    filename = os.path.join(latest, result['filename'])
    if not os.path.exists(filename):
        print('%s is not found in latest folder.' % filename)
        continue

    if os.stat(filename).st_size == 0:
        print('%s is empty, skipping.' % filename)
        continue

    charge_type = 'standard'
    if "drg" in filename.lower():
        charge_type = "drg"

    if result['filename'] in seen:
        continue

    seen.append(result['filename'])

    print("Parsing %s" % filename)

    if filename.endswith('xlsx'):

        # has counts, description, procedure type (not costs)
        if "common25" in filename.lower():
            continue

        # Unfortunately cdm_all files are inconsistent, would need custom parsing (for sheets) each
        elif "cdm_all" in filename.lower():
            continue

        # ['Charge Code', 'Charge Description', 'Charge Amount', 'Comments']
        elif "106071018_CDM" in filename or "106070988_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'Charge Description'
            price_key = 'Charge Amount' 
            code_key = 'Charge Code'

        # ['Charge Code', 'Charge Description', 'Price', 'Comments']
        elif "106074039_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'Charge Description'
            price_key = 'Price' 
            code_key = 'Charge Code'

        # ['Description', 'Code', 'Unnamed: 2', 'Unnamed: 3', 'Price', 'Tier  Code', 'Dept', 'Subd', 'Elem', 'Stat']
        # Writing over row of dashes ----
        elif "106420491_CDM" in filename:
             content = pandas.read_excel(filename, skiprows=2)
             content.columns = ['Description', 
                                'Code', 
                                'Unnamed: 2', 'Unnamed: 3', 
                                'Price', 
                                'Tier  Code', 
                                'Dept', 
                                'Subd', 
                                'Elem', 
                                'Stat']
            description_key = 'Description'
            price_key = 'Price' 
            code_key = 'Code'

        # ['Fac', 'Charge #', 'Description', 'Price', 'GL Key']
        elif "106301357_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=5)
            description_key = 'Description'
            price_key = 'Price' 
            code_key = 'Charge #'

        # ['Chrg Code', 'Chrg Desc', 'Chrg Amt IP', 'Chrg Amt OP']
        elif "106430779_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=5)
            description_key = 'Chrg Desc'
            code_key = 'Chrg Code'
            for row in content.iterrows():

                # Outpatient
                idx = df.shape[0] + 1
                entry = [row[1][code_key],             # charge code
                         row[1]['Chrg Amt OP'],        # price
                         row[1][description_key],      # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         'outpatient']            
                df.loc[idx,:] = entry

                # Inpatient
                idx = df.shape[0] + 1
                entry = [row[1][code_key],             # charge code
                         row[1]['Chrg Amt IP'],        # price
                         row[1][description_key],      # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         'inpatient']            
                df.loc[idx,:] = entry

        # ['Charge code', 'Charge Description', 'Charge Cat', 'Previous Price', 'Current Price', 'UOS', 'Charges', 'Change', '% Change', 'Note'],
        elif "106190449_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=1)
            description_key = 'Charge Description'
            price_key = 'Current Price' 
            code_key = 'Charge code'

        # ['CDM NO', 'DISPENSED DESCRIPTION', 'PRICE ', 'TYPE', 'NOTE'
        elif "106331152_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'DISPENSED DESCRIPTION'
            price_key = 'PRICE ' 
            code_key = 'CDM NO'

        # ['Charge Description', 'Price', 'Comment']
        elif "106430763_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'Charge Description'
            price_key = 'Price' 
            code_key = None

        # ['Item # ', 'Description', 'Unit of Measure', 'Patient Charge']
        elif "106331168_CDM(2)" in filename:
            content = pandas.read_excel(filename)
            description_key = 'Description'
            price_key = 'Patient Charge' 
            code_key = 'Item # '

        # ['Procedure Code', 'Description', 'Unit Price']
        elif "106331168_CDM(1)" in filename:
            content = pandas.read_excel(filename, skiprows=3)
            description_key = 'Description'
            price_key = 'Unit Price'
            code_key = 'Procedure Code'

        # ['Item\nNumber', '\nDescription', '\nBegin Date ', '\nEnd Date', '\nUnits', '\nCharge By', '\nCost', 'Base Price/\nMarkup']
        elif "106196404_CDM(1)" in filename:
            content = pandas.read_excel(filename, skiprows=5)
            description_key = '\nDescription'
            price_key = '\nCost'
            code_key = None

        elif "106196404_CDM(2)" in filename:
            content = pandas.read_excel(filename, skiprows=5)
            description_key = '\nDescription'
            price_key = '\nCost'
            code_key = None

        # ['CDMCHRG#', 'CDMDSC', 'NEWPRICE', 'STAT']
        elif "106440755_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'CDMDSC'
            price_key = 'NEWPRICE'
            code_key = 'CDMCHRG#'

        # ['Code', 'Description', 'Code.1', '  Amount  ']
        elif "106190256_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=4)
            description_key = 'Description'
            price_key = '  Amount  '
            code_key = 'Code'
 
        # ['PROC (CDM)', 'DRUG DESCRIPTION', 'CHARGE']
        elif "106364231_CDM_RX" in filename:
            content = pandas.read_excel(filename, skiprows=7)
            description_key = "DRUG DESCRIPTION"
            price_key = "CHARGE"        
            code_key = 'PROC (CDM)'

        # 'Charge Code', 'Description', 'CPT Code', 'Rate'
        elif "106070924_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=3)
            description_key = "Description"
            price_key = "Rate"        
            code_key = "Charge Code"

        #  Code       Description Code.1   Amount
        elif "106190766_CDM" in filename or "106190197_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=4)
            description_key = "Description"
            price_key = "Amount"        
            code_key = "Code"

        # ['PROC_NAME', 'CHARGE_AMOUNT', 'COMMENT', 'Unnamed: 3']
        elif "106304409_CDM" in filename or "106196035_CDM" in filename or "106196403_CDM" in filename or "106361223_CDM" in filename or "106014132_CDM" in filename or "106104062_CDM" in filename or  "106190429_CDM" in filename or "106394009_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = "PROC_NAME"
            price_key = "CHARGE_AMOUNT"        
            code_key = None

        # ['CDM#', 'CDM Description', 'Facility', 'gl_account_id', 'Rev Code', 'Price', 'CPT/HCPCS']
        elif "106301188_CDM" in filename or "106301140_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=1)
            description_key = "CDM Description"
            price_key = "Price"        
            code_key = "CDM#"

        # ['CDM #', 'Description', 'Price']
        elif "106190298_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=4)
            description_key = 'Description'
            price_key = "CDM #"
            code_key = 'Price'

        # ['CHARGE #', 'DESC', 'REV', 'CPT', 'PRICE', 'Unnamed: 5']
        elif "106220733_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=4)
            description_key = 'DESC'
            price_key = 'PRICE'
            code_key = 'CHARGE #'

        # ['PROC (CDM)', 'CHG CAT', 'ARMC REV DEPT', 'PROCEDURE (CDM) DESCRIPTION', 'CHARGE', 'CPT-4', 'MCLcde']
        elif "106364231_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=7)
            description_key = 'PROCEDURE (CDM) DESCRIPTION'
            price_key = "CHARGE"
            code_key = 'PROC (CDM)'

       #['PROCEDURE', 'DESCRIPTION', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'STD AMOUNT']
        elif "106010887_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=3)
            description_key = "DESCRIPTION"
            price_key = "STD AMOUNT"
            code_key = "PROCEDURE"

        # ['PROC_NAME', 'CHARGE_AMOUNT', 'COMMENT']
        elif "106074097_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=1)
            description_key = "PROC_NAME"
            price_key = "CHARGE_AMOUNT"
            code_key = None

        # Service ID', 'User Gen. Service ID', 'Service Name', 'Effective Date', 'Price ($)'
        elif "106474007_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=1)
            description_key = "Service Name"
            price_key = "Price ($)"
            code_key = 'Service ID'

        # ['Code ', 'Procedure_Name', 'Cost']
        elif "106304159_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=2)
            description_key = "Procedure_Name"
            price_key = "Cost"
            code_key = 'Code '

        elif "106301127_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = "chg_desc"
            price_key = "chg_amt_1"
            code_key = "chg_code"

        # ['PROCEDURE', 'DESCRIPTION', 'DEPARTMENT', 'CHG CAT', 'COST', 'STD AMOUNT  CPT      HCPC', 'A']
        elif "106331194_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = "DESCRIPTION"
            price_key = 'STD AMOUNT  CPT      HCPC'
            code_key = "PROCEDURE"

        elif "106370749_" in filename:
            content = pandas.read_excel(filename)
            description_key = "Description"
            price_key = "Patient Price"
            code_key = None   

        # ['Level of Care', 'Begin Date', 'End Date', 'Charge By', 'Base Price ', 'Unnamed: 5']
        elif "106196404_CDM(4)" in filename:
            content = pandas.read_excel(filename, skiprows=6)
            description_key = 'Level of Care'
            price_key = 'Base Price '
            code_key = None

        elif "106196404_CDM(3)" in filename:
            content = pandas.read_excel(filename, skiprows=7)
            description_key = 'Level of Care'
            price_key = 'Base Price '
            code_key = None

        # ['PROC (CDM)', 'DRUG DESCRIPTION', 'CHARGE']
        elif "106364231_CDM_RX" in filename:
            content = pandas.read_excel(filename, skiprows=7)
            description_key = "DRUG DESCRIPTION"
            price_key = "CHARGE"
            code_key = 'PROC (CDM)' 

        # ['CHARGE #', 'CHARGE DESCRIPTION', 'CPT-4', 'PT CHG $', 'INS CD']
        elif "106301155_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=4)
            code_key =  'CHARGE #'
            description_key = 'CHARGE DESCRIPTION'
            price_key = 'PT CHG $'

        # ['Reference ID', 'Description', 'Price']
        elif "106364014_CDM" in filename or "106364502_CDM" in filename or "106361246_CDM" in filename or "106334589_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=4)
            code_key =  'Reference ID'
            description_key = 'Description'
            price_key = 'Price'

        elif "106090793_CDM_RX" in filename:
            content = pandas.read_excel(filename)
            additional_row = content.columns.tolist()
            idx = content.shape[0] + 1
            content.loc[idx] = additional_row
            content.columns = ['DESCRIPTION', "CODE", "PRICE"]
            code_key = "CODE"
            description_key = "DESCRIPTION"
            price_key = 'PRICE'
 
        # ['Unnamed: 0', 'CHARGE CODE', 'CHARGE DESCRIPTION', 'PRICE', 'Unnamed: 4']
        elif "106130699_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=6)
            code_key = "CHARGE CODE"
            description_key = "CHARGE DESCRIPTION"
            price_key = 'PRICE'

        elif "106090793_CDM" in filename:
            # ['EAP PROC CODE', 'CODE DESCRIPTION', 'CPT', 'REV CODE', 'UNIT CHARGE AMOUNT']
            content = pandas.read_excel(filename)
            code_key = "CPT"
            description_key = "CODE DESCRIPTION"
            price_key = 'UNIT CHARGE AMOUNT'

        elif "106190555_CDM" in filename:
            # 'Charge\nCode', 'Description', 'CPT/ HCPCS\nCode', 'OP/ Default Price', 'IP/ER\nPrice'
            content = pandas.read_excel(filename, skiprows=4)
            code_key = 'Charge\nCode'
            description_key = "Description"
            for row in content.iterrows():

                # Outpatient
                idx = df.shape[0] + 1
                entry = [row[1][code_key],             # charge code
                         row[1]['OP/ Default Price'],  # price
                         row[1][description_key],      # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         'outpatient']            
                df.loc[idx,:] = entry

                # Inpatient
                idx = df.shape[0] + 1
                entry = [row[1][code_key],             # charge code
                         row[1]['IP/ER\nPrice'],            # price
                         row[1][description_key],      # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         'inpatient']            
                df.loc[idx,:] = entry

            continue

        elif "cdm_" in filename.lower():
            # ['2018 Charge Codes', 'Charge Codes Description', 'HCPCS Codes', 'June 2018 Prices']
            content = pandas.read_excel(filename, skiprows=4)
            code_key =  '2018 Charge Codes'
            description_key = 'Charge Codes Description'
            price_key = 'June 2018 Prices'

            if code_key not in content.columns.tolist():
                code_key = None
                description_key = 'Description'
                price_key = 'Patient Price'

                if description_key not in content.columns.tolist():
                    content = pandas.read_excel(filename)
                    description_key = "PROC_NAME"
                    price_key = "CHARGE_AMOUNT"        
                    code_key = None

                if description_key not in content.columns.tolist():
                    description_key = "DESCRIPTION"
                    price_key = "STD AMOUNT"        
                    code_key = "PROCEDURE"


        elif "cdm(" in filename.lower():
            # CDM #                    Description   Price
            content = pandas.read_excel(filename, skiprows=4)
            code_key = "CDM #"
            description_key = "Description"
            price_key = "Price"

        elif "pct_chg" in filename.lower():
            continue

        elif "drg" in filename.lower():
            #['Hospital', 'MS DRG', 'MS DRG Desc', 'Rank', 'Cases', 'Total Charges', 'Avg Chrg / Case']
            content = pandas.read_excel(filename, skiprows=8)
            code_key = "MS DRG"
            description_key = "MS DRG Desc"
            price_key = 'Avg Chrg / Case'

        else:
            continue

        for row in content.iterrows():
            if code_key != None:
                code = row[1][code_key]
            else:
                code = None
            price = row[1][price_key]
            if pandas.isnull(price):
                continue
            idx = df.shape[0] + 1
            entry = [code,                         # charge code
                     price,            # price
                     row[1][description_key],      # description
                     result["hospital_id"],        # hospital_id
                     result['filename'],
                     charge_type]            
            df.loc[idx,:] = entry

        # When we get to index 350 (hospital_id 'kaiser-foundation-hospital---walnut-creek')
        # It's time to save and start a new data file, we just hit the max Github file size
        if result['hospital_id'] == 'kaiser-foundation-hospital---walnut-creek':

            # Remove empty rows
            df = df.dropna(how='all')

            # Save data!
            print(df.shape)
            df.to_csv(output_data, sep='\t', index=False)
            df.to_csv(output_year, sep='\t', index=False)
            output_data = os.path.join(here, 'data-latest-2.tsv')
            output_year = os.path.join(here, 'data-%s-2.tsv' % year)
            df = pandas.DataFrame(columns=columns)
