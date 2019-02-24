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
for r in range(0, len(results)):
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

        # ['CDM', 'Description', 'Standard Charge', 'Surgery Center/Procedure Room Charge', 'L&D Charge', 'Supply Charge Range']
        elif "106190930_CDM" in filename or "106190687_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'Description'
            price_key = 'Standard Charge'
            code_key = 'CDM'

        # ['NDC ID', 'NDC_CODE', 'RAW_11_DIGIT_NDC', 'RAW_NDC_CODE',
        # 'Medication ID', 'Medication Name', 'PACKAGE_SIZE', 'MED Units',
        # 'PACKAGE_QUANTITY', 'PRICE_CODE_C', 'Price COde', 'PRICE',
        # 'PRICE_PER_UNIT_YN']
        elif "106370782_CDM_Rx" in filename:
            content = pandas.read_excel(filename)

            # This distinguishes between inpatient / outpatient price code
            # ['Inpt/Contract Costs', 'Outpatient Cost']

            for row in content.iterrows():
 
                charge_type = 'outpatient'
                if row[1]['Price COde'] == 'Inpt/Contract Costs':
                    charge_type = 'inpatient'

                    idx = df.shape[0] + 1
                    entry = [row[1]['PRICE_CODE_C'],       # charge code
                             row[1]['PRICE'],        # price
                             row[1]['Medication Name'],      # description
                             result["hospital_id"],        # hospital_id
                             result['filename'],
                             charge_type]     
                    df.loc[idx,:] = entry

            continue


        #['CHG CODE', 'BILLING DESC', 'DEPT',
        #' 2017 Price Per Unit for Infussion and Pharmacy',
        #'2018 Price Per Unit for Infussion and Pharmacy',
        #'Infussion and Pharmacy Price Change', '2018 Current PRICE',
        # '2017 PRICE', 'Price Difference', 'CPT']
        elif "106130760_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'BILLING DESC'
            price_key = '2018 Current PRICE'
            code_key = 'CHG CODE'

        # ['MNEMONIC', 'DESCRIPTION', 'PRICE']
        elif "106540798_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=4)
            description_key = 'DESCRIPTION'
            price_key = 'PRICE' 
            code_key = 'MNEMONIC'

        # ['Procedure Code', 'Procedure Name', 'Revenue Code', 'Price']
        elif "106370673_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'Procedure Name'
            price_key = 'Price' 
            code_key = 'Revenue Code'

        # ['Count', 'Description', 'Procedure Type']
        # Doesn't have prices
        elif "106560508_CDM" in filename or "106560529_CDM" in filename:
            continue

        # ['CHARGE CODE', 'CHARGE DESCRIPTION', 'CHARGE AMOUNT ']
        elif "106010967_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=1) 
            description_key = 'CHARGE DESCRIPTION'
            price_key = 'CHARGE AMOUNT ' 
            code_key = 'CHARGE CODE'


        # ['Description', 'FY -17 Facility Rate', 'FY-17 Professional Rate']
        elif "106560481_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=3) 
            description_key = 'Description'
            price_key = 'FY -17 Facility Rate'
            code_key = None

        # ['Charge Code', 'Description', 'Std Charge', 'Outpt Charge', 'Comment']
        elif "106190680_CDM" in filename or "106190756_CDM" in filename or "106190758_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=3) 
            description_key = 'Description'
            price_key = 'Std Charge' 
            code_key = 'Charge Code'

        # ['Charge Code', 'Charge Description', 'Charge Amount', 'Comments']
        elif "106071018_CDM" in filename or "106070988_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'Charge Description'
            price_key = 'Charge Amount' 
            code_key = 'Charge Code'

        # ['Item ID', 'Item Name', 'External IDs', 'Alias', 'Active?',
        # 'Effective Date', 'Description', 'Supply or Drug?', 'Type of Item',
        # 'LDA Type', 'Reusable?', 'OR Location', 'Inv Location', 'Supplier',
        # 'Supplier Catalog No.', 'Supplier Price', 'Supplier Pkg Type',
        # 'Supplier Pkg to Shelf Ratio', 'Last Supplier', 'Last Catalog No.',
        # 'Last Purchase Price', 'Manufacturer', 'Manuf Catalog No.',
        # 'Manuf Pkg to Shelf Ratio', 'Order Ratio', 'Order Pack Type', 'GTINs',
        # 'Used by Areas', 'Chargeable', 'Charge Code EAP', 'Charge Code FT',
        # 'Charge Per Unit', 'Cost Per Unit', 'Unnamed: 33']
        elif "106370782_CDM(2)" in filename:
            content = pandas.read_excel(filename, skiprows=3)
            description_key = 'Item Name'
            price_key = 'Cost Per Unit'
            code_key = 'Item ID'

        # ['CDM#', 'CDM Description', 'Facility', 'gl_account_id', 'gl_sub_acct',
        #'chg_type_int_id', 'cod_dtl_ds', 'active_dt', 'Rev Code', 'Price',
        # 'CPT/HCPCS', 'Unnamed: 11']
        elif "106301258_CDM" in filename or "106361370_CDM_" in filename:
            content = pandas.read_excel(filename, skiprows=1)
            description_key = 'CDM Description'
            price_key = 'Price'
            code_key = 'CDM#'

        # ['IVNUM', 'IVDESC', 'CPT', 'Price', 'Clinic']
        elif "106321016_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'IVDESC'
            price_key = 'Price'
            code_key = 'CPT'

        # ['GL', 'Bill Item Activity Type', 'PS:Price Sched Price', 'Description', 'SJGH_CDM']
        elif "106391010_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'Description'
            price_key = 'PS:Price Sched Price'
            code_key = 'SJGH_CDM'

        # ['procedure status', 'procedure master #', 'procedure name', 'Default',
        #'Trauma variants', 'OP Rx (not in  Pharmacy file)',
        #'OP Rx (not in  Pharmacy file, MediCal only)', 'Note']
        elif "106370782_CDM(1)" in filename:
            content = pandas.read_excel(filename)
            description_key = 'procedure name'
            price_key = 'Default'
            code_key = 'procedure master #'

        # ['Charge Code', 'Charge Description', 'Price', 'Comments']
        elif "106074039_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'Charge Description'
            price_key = 'Price' 
            code_key = 'Charge Code'

        # ['Chrg Dept', 'Chrg Code', 'Chrg Bill Desc', 'Chrg Rev Code',
        # 'Chrg HCPCS Proc', 'Chrg CPT Code', 'Chrg Amt IP', 'Chrg Amt OP',
        # 'Chrg Type']
        elif "106560492_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=6)
            description_key = 'Chrg Bill Desc'
            code_key = 'Chrg Code'

            for row in content.iterrows():
 
                if not pandas.isnull(row[1]['Chrg Amt OP']):
                    # Outpatient
                    idx = df.shape[0] + 1
                    entry = [row[1][code_key],             # charge code
                             row[1]['Chrg Amt OP'],        # price
                             row[1][description_key],      # description
                             result["hospital_id"],        # hospital_id
                             result['filename'],
                             'outpatient']            
                    df.loc[idx,:] = entry

                if not pandas.isnull(row[1]['Chrg Amt IP']):
                    # Inpatient
                    idx = df.shape[0] + 1
                    entry = [row[1][code_key],             # charge code
                             row[1]['Chrg Amt IP'],        # price
                             row[1][description_key],      # description
                             result["hospital_id"],        # hospital_id
                             result['filename'],
                             'inpatient']            
                    df.loc[idx,:] = entry
            continue

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

        # ['Charge Code', 'Charge Description', 'Charge Code and Description', 'org_nm', 'gl_account_id', 'gl_sub_acct', 'NRV', 'Charge Amount', 'CPT']
        elif "106450936_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'Charge Description'
            price_key = 'Charge Amount' 
            code_key = 'Charge Code'

        # ['CDM', 'Description', 'Standard Charge', 'Surgery Center/Procedure Room Charge', 'L&D Charge', 'Supply Charge Range']
        elif "106190796_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'Description'
            price_key = 'Standard Charge' 
            code_key = 'CDM'


        # ['Charge Code ', 'Description', 'Primary Price', 'Comments']
        elif "106434040_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=5)
            description_key = 'Description'
            price_key = 'Primary Price' 
            code_key = 'Charge Code '
 
        # ['Fac', 'Charge #', 'Description', 'Price', 'GL Key']
        elif "106301357_CDM" in filename or "106190570_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=5)
            description_key = 'Description'
            price_key = 'Price' 
            code_key = 'Charge #'

        # ['CDM/SPSI', 'SERVICE DESCRIPTION', 'RATE TYPE', 'PRICE PER UNIT',
        # 'MIN UNIT', 'START VALUE1', 'STOP VALUE1', 'MIN PER UNIT1',
        # 'UNIT PRICE1', 'START VALUE2', 'STOP VALUE2', 'MIN PER UNIT2',
        # 'UNIT PRICE2', 'START VALUE3', 'STOP VALUE3', 'MIN PER UNIT3',
        # 'UNIT PRICE3']
        elif "106190630_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=3)
            description_key = 'SERVICE DESCRIPTION'
            price_key = 'PRICE PER UNIT' 
            code_key = 'CDM/SPSI'

        # ['BILL ITEM ID', 'LONG DESCRIPTION', 'CPT-4', 'HCPCS', 'REVENUE',
        # 'TMMC Standard Price Schedule', 'TMMC OP Lab Price Schedule']
        elif "106190422_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'LONG DESCRIPTION'
            code_key = 'BILL ITEM ID'
            price_key = 'TMMC Standard Price Schedule'

        # ['Chg Code', 'Chrg Description', 'ref_eff_ts', 'row_sta_cd',
        # 'table_int_id', 'ref_int_id', 'org_int_id', 'lst_mod_id', 'lst_mod_ts',
        # 'compute_0010', 'org_nm', 'gl_account_id', 'gl_sub_acct',
        # 'chg_type_int_id', 'cod_dtl_ds', 'active_dt', 'Rev Code', 'Price',
        # 'CPT/HCPCS', 'gl_stat']
        elif "106334018_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=1)
            description_key = 'Chrg Description'
            code_key = 'Chg Code'
            price_key = 'Price'

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

        #  ['Group', 'ChargeCode', 'ChargeCode Description', 'Fee Schedule Charge 1']
        elif "106370875_CDM" in filename or "106370689_CDM" in filename or "106370714_CDM" in filename or "106370694_CDM" in filename or "106370745_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'ChargeCode Description'
            price_key = 'Fee Schedule Charge 1'
            code_key = 'ChargeCode'


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

        # ['Fac', 'Charge #', 'Description', 'Price', 'GL Key'],
        elif "106190380_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=5)
            description_key = 'Description'
            price_key = 'Price' 
            code_key = 'Charge #'

        # ['CDM NO', 'DISPENSED DESCRIPTION', 'PRICE', 'TYPE', 'NOTE']
        elif "106334068_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'DISPENSED DESCRIPTION'
            price_key = 'PRICE' 
            code_key = 'CDM NO'

        # ['Charge Code', 'Charge Description', 'CPT-4', 'Amount']
        elif "106190110_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=5)
            description_key = 'Charge Description'
            price_key = 'Amount' 
            code_key = 'Charge Code'

        # ['ITEM #', 'DESCRIPTION', 'PRICE', 'CPT CODE']
        elif "106040937_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=2)
            description_key = 'DESCRIPTION'
            price_key = 'PRICE' 
            code_key = 'ITEM #'

        # ['Item # ', 'Description', 'Unit of Measure', 'Patient Charge']
        elif "106331168_CDM(2)" in filename:
            content = pandas.read_excel(filename)
            description_key = 'Description'
            price_key = 'Patient Charge' 
            code_key = 'Item # '

        # ['Fac', 'Charge #', 'Description', 'Price', 'GL Key']
        elif "106190198_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=5)
            description_key = 'Description'
            price_key = 'Price'
            code_key = 'Charge #'

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
        elif "106190766_CDM" in filename or "106190197_CDM" in filename or "106190521_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=4)
            content.columns = ['Code', 'Description', 'Code.1', 'Amount']
            description_key = "Description"
            price_key = "Amount"        
            code_key = "Code"

        # ['PROC_CODE', 'PROC_NAME', 'INPAT_FEE', 'OUTPAT_FEE']
        elif "106090933_CDM" in filename:
            content = pandas.read_excel(filename)

            for row in content.iterrows():
                # Outpatient
                idx = df.shape[0] + 1
                price_key = 'OP/Default Price'
                entry = [row[1]['PROC_CODE'],             # charge code
                         row[1]['OUTPAT_FEE'],  # price
                         row[1]['PROC_NAME'],      # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         'outpatient']            
                df.loc[idx,:] = entry

                # Inpatient
                idx = df.shape[0] + 1
                entry = [row[1]['PROC_CODE'],             # charge code
                         row[1]['INPAT_FEE'],            # price
                         row[1]['PROC_NAME'],      # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         'inpatient']            
                df.loc[idx,:] = entry

            continue


        # ['PROC_NAME', 'CHARGE_AMOUNT', 'COMMENT', 'Unnamed: 3']
        elif "106304409_CDM" in filename or "106196035_CDM" in filename or "106196403_CDM" in filename or "106361223_CDM" in filename or "106014132_CDM" in filename or "106104062_CDM" in filename or  "106190429_CDM" in filename or "106394009_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = "PROC_NAME"
            price_key = "CHARGE_AMOUNT"        
            code_key = None

        # ['CDM #', 'CDM Description', 'gl_account_id', 'Account Name',
        # 'gl_sub_acct', 'chg_type_int_id', 'Charge Type', 'active_dt',
        # 'Rev Code', 'Price', 'CPT or HCPCS CD', 'Price.1']
        elif "106301566_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=1)
            description_key = "CDM Description"
            price_key = "Price"        
            code_key = "CDM #"


        # ['CDM NO', 'DISPENSED DESCRIPTION', 'PRICE', 'TYPE', 'NOTE']
        elif "106334564_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = "DISPENSED DESCRIPTION"
            price_key = "PRICE"  
            code_key = "CDM NO"


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

        # ['CDM NO', 'DISPENSED DESCRIPTION', 'PRICE ', 'TYPE', 'NOTE']
        elif "106196405_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = "DISPENSED DESCRIPTION"
            price_key = "PRICE "
            code_key = "CDM NO"

        # ['PROC_NAME', 'CHARGE_AMOUNT', 'COMMENT']
        elif "106074097_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=1)
            description_key = "PROC_NAME"
            price_key = "CHARGE_AMOUNT"
            code_key = None

        # ['Charge Code', 'Description', 'Std Charge', 'Outpt Charge', 'Comment']
        elif "106190385_CDM" in filename or "106190470_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=3)
            description_key = "Description"
            price_key = "Std Charge"
            code_key = 'Charge Code'

        # Service ID', 'User Gen. Service ID', 'Service Name', 'Effective Date', 'Price ($)'
        elif "106474007_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=1)
            description_key = "Service Name"
            price_key = "Price ($)"
            code_key = 'Service ID'

        elif "106201281_CDM" in filename:
            content = pandas.read_excel(filename)
            additional_row = content.columns.tolist()
            idx = content.shape[0] + 1
            content.loc[idx] = additional_row
            content.columns = ["CODE", 'DESCRIPTION', "PRICE"]
            code_key = "CODE"
            description_key = "DESCRIPTION"
            price_key = 'PRICE'

        # ['Charge#', 'Description', 'Charge Price', 'Unnamed: 3']
        elif "106260011_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=6)
            description_key = "Description"
            price_key = "Charge Price"
            code_key = 'Charge#'

        # ['Code ', 'Procedure_Name', 'Cost']
        elif "106304159_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=2)
            description_key = "Procedure_Name"
            price_key = "Cost"
            code_key = 'Code '

        # ['PROCEDURE', 'DESCRIPTION', 'DEPARTMENT', 'CHG CAT', 'COST', 'STD AMOUNT  CPT      HCPC', 'A']
        elif "106301127_CDM" in filename:
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

        # ['CHARGE CODE', 'BILLING DESCRIPTION', 'CHARGE PRICE TIER 1', 'CHARGE PRICE TIER 2']
        elif "106211006_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = 'BILLING DESCRIPTION'
            price_key = 'CHARGE PRICE TIER 1'
            code_key = 'CHARGE CODE'

        elif "106196404_CDM(3)" in filename:
            content = pandas.read_excel(filename, skiprows=7)
            description_key = 'Level of Care'
            price_key = 'Base Price '
            code_key = None

        # ['CDM', 'CDM DESCRIPTION', 'CPT/HCPC', 'OP', 'IP', 'FQHC', 'LAB OP',
        # 'LAB IP', 'RAD OP', 'RAD IP']
        elif "106301279_CDM" in filename:
            content = pandas.read_excel(filename)
            description_key = "CDM DESCRIPTION"
            code_key = 'CDM' 

            for row in content.iterrows():

                # Outpatient
                if row[1]['OP'] != 0:
                    idx = df.shape[0] + 1
                    entry = [row[1][code_key],             # charge code
                             row[1]['OP'], # price
                             row[1][description_key],      # description
                             result["hospital_id"],        # hospital_id
                             result['filename'],
                             'outpatient']            
                    df.loc[idx,:] = entry

                if row[1]['IP'] != 0:
                    idx = df.shape[0] + 1
                    entry = [row[1][code_key],             # charge code
                             row[1]['IP'],                 # price
                             row[1][description_key],      # description
                             result["hospital_id"],        # hospital_id
                             result['filename'],
                             'inpatient']            
                    df.loc[idx,:] = entry

            continue

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
        elif "106364014_CDM" in filename or "106334589_CDM" in filename or "106361246_CDM" in filename or "106364502_CDM" in filename:
            content = pandas.read_excel(filename)
            code_key =  'Reference ID'
            description_key = 'Description'
            price_key = 'Price'


        # ['Reference ID', 'Description', 'Price']
        elif "106364014_CDM" in filename:
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

        # ['Charge Code', 'Charge Description', 'CPT/HCPCS Code',
        # 'Inpatient \nPrice', 'Outpatient \nPrice']
        elif "106341006_CDM" in filename:
            content = pandas.read_excel(filename, skiprows=5)
            code_key = 'Charge Code'
            description_key = "Charge Description"

            for row in content.iterrows():

                # Outpatient
                idx = df.shape[0] + 1
                entry = [row[1][code_key],             # charge code
                         row[1]['Outpatient \nPrice'], # price
                         row[1][description_key],      # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         'outpatient']            
                df.loc[idx,:] = entry

                # Inpatient
                idx = df.shape[0] + 1
                entry = [row[1][code_key],             # charge code
                         row[1]['Inpatient \nPrice'],  # price
                         row[1][description_key],      # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         'inpatient']            
                df.loc[idx,:] = entry

            continue



        elif "106190555_CDM" in filename or "106190500_CDM" in filename:
            # 'Charge\nCode', 'Description', 'CPT/ HCPCS\nCode', 'OP/ Default Price', 'IP/ER\nPrice'
            content = pandas.read_excel(filename, skiprows=4)
            code_key = 'Charge\nCode'
            description_key = "Description"
            for row in content.iterrows():

                # Outpatient
                idx = df.shape[0] + 1
                price_key = 'OP/Default Price'
                if price_key not in content.columns.tolist():
                    price_key = 'OP/ Default Price'
                entry = [row[1][code_key],             # charge code
                         row[1][price_key],  # price
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

                if code_key not in content.columns.tolist():
                    content = pandas.read_excel(filename, skiprows=3) 
                    description_key = 'Description'
                    price_key = 'Std Charge' 
                    code_key = 'Charge Code'


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
            print(df.shape)  # 757
            df.to_csv(output_data, sep='\t', index=False)
            df.to_csv(output_year, sep='\t', index=False)
            output_data = os.path.join(here, 'data-latest-2.tsv')
            output_year = os.path.join(here, 'data-%s-2.tsv' % year)
            df = pandas.DataFrame(columns=columns)


# One final save
print(df.shape)
df.to_csv(output_data, sep='\t', index=False)
df.to_csv(output_year, sep='\t', index=False)
