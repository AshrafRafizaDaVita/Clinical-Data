import pandas as pd
import numpy as np
import os
from config import APAC_DIRECTORIES, DATA_FOLDER
from datetime import datetime

# To convert from '2024-11' to '2024_Nov
def convert_date(date):
    # Input string
    date_str = date

    # Convert to datetime object
    date_obj = datetime.strptime(date_str, '%Y-%m')

    # Format to desired output
    formatted_date = date_obj.strftime('%Y_%b')

    return formatted_date



# Read APAC data from Shared Folder
# Read and combine APAC files from APAC folder
def read_apac_folders(month):
    selected_month = month
    apac_dir = pd.read_excel(APAC_DIRECTORIES)
    apac = []

    # Iterate through each row in the DataFrame
    for index, row in apac_dir.iterrows():
        region = row["Region"]
        center = row["Center"]
        link = row["Link"]

        if os.path.exists(link):
            files = os.listdir(link)
            for filename in files:
                if ((filename.startswith(selected_month)) & (filename.endswith('.xlsx'))):
                    filepath = os.path.join(link, filename)
                    print(f"Link Exist Region {region} {center}: {filepath}")
                    df= pd.read_excel(filepath, skiprows=7)

                    # Add Center Name column
                    center = filename.split('_')[2]
                    df['Center Name'] = center

                    # Extract month and year from the file name using regular expressions
                    # Split the file name based on underscores
                    file_parts = filename.split('_')

                    # Extract year and month parts from the file name
                    year_part = file_parts[0]
                    month_part = file_parts[1]

                    # Convert month abbreviation to month number
                    month_num = datetime.strptime(month_part, "%b").month

                    # Create a datetime object with the extracted month and year
                    reporting_date = datetime(int(year_part), month_num, 1)

                    # Convert the datetime object to the desired format (1/2/2024)
                    reporting_month = reporting_date.strftime("%d/%m/%Y")

                    df['Reporting Month'] = reporting_month

                    apac.append(df)
        else:
            print(f"Directory not found for Region {region}, Center {center}")

    combined_df = pd.concat(apac, ignore_index=True)
    combined_df['Draw Date'] = pd.to_datetime(combined_df['Draw Date'], format='%d/%m/%Y', errors='coerce')

    # Rename the column 'MR NO(if teammate, tag as TEAMMATE, if new patient tag as NEW)' to 'MR NO'
    combined_df = combined_df.rename(columns={'MR NO(if teammate, tag as TEAMMATE, if new patient tag as NEW)': 'MR No.'})

    # Print unique Centers
    print(f"\nTotal Centers: {len(combined_df['Center Name'].unique())}")

    return combined_df



# Check for Blank Cells in APAC
def check_blanks(df):
    # Columns to check
    columns_to_check = [
        'MR No.', 
        'Tx Duration (mins)', 
        'Pre Tx Weight (Kg)', 
        'Post Tx Weight (Kg)', 
        # 'SP Kt/V', 
        # 'Targe UF', 
        # 'URR', 
        'QB (mL/min)', 
        'Primary'
    ]

    # Create a DataFrame to store rows with any blank values
    blank_rows_list = []

    # Create a DataFrame to store rows with any blank values
    blank_rows_df = pd.DataFrame(columns=columns_to_check)

    # Iterate over each row
    for index, row in df.iterrows():
        # Check if any of the specified columns have blank values in the current row
        if row['MR No.'] not in ['TEAMMATE', 'NEW']:
            if row[columns_to_check].isnull().any():
                # If any blank value is found, add the row to the blank_rows_df
                # blank_rows_df = blank_rows_df.append(row, ignore_index=True)
                blank_rows_list.append(row)

    # Display the DataFrame containing rows with any blank values
    blank_rows_df = pd.DataFrame(blank_rows_list, columns=df.columns)

    # Print center with blanks
    print(f"\nCenter with blank: {blank_rows_df['Center Name'].unique()}")

    return blank_rows_df



# Check for value errors in APAC
# Check blanks
def check_values(df):
    # Columns to check
    columns_to_check = [
        'Pre Tx Weight (Kg)', 
        'Post Tx Weight (Kg)', 
        'Targe UF', 
        'QB (mL/min)',
        'SP Kt/V', 
        'URR',
        'MR NO'
    ]

    # Create a DataFrame to store rows with any blank values
    error_list = []

    # Create a DataFrame to store rows with any blank values
    error_rows_df = pd.DataFrame(columns=columns_to_check)

    # Convert 'MR NO' column to string type
    df['MR No.'] = df['MR No.'].astype(str)

    # Iterate over each row
    for index, row in df.iterrows():
        # Check if any of the specified columns have blank values in the current row
        if row['MR No.'] not in ['TEAMMATE', 'NEW']:

            # Check Item 1 - PRE TX WEIGHT
            # if (row[columns_to_check[0]] < 30) & (row[columns_to_check[0]] > 200):
            if not ((30 <= row[columns_to_check[0]] <= 200)):
                print(f'\nPre Weight Invalid : {row['MR No.']}, {row['Center Name']}, {row[columns_to_check[0]]} Kg')
                error_list.append(row)

            # Check Item 2 - POST TX WEIGHT
            # if (row[columns_to_check[1]] < 30) & (row[columns_to_check[1]] > 200):
            if not (30 <= row[columns_to_check[1]] <= 200):
                print(f'\nPost Weight Invalid : {row['MR No.']}, {row['Center Name']}, {row[columns_to_check[1]]} Kg')
                error_list.append(row)

            # Item 3 - TARGET UF
            try:
                if ((row[columns_to_check[2]] <= 0) | (row[columns_to_check[2]] > 10)):
                    print(f'\nTarget UF Invalid : {row['MR No.']}, {row['Center Name']}, {row[columns_to_check[2]]}')
                    error_list.append(row)

            except Exception as e:
                print(f"Error encountered in Center: {row['Center Name']} - {e}")

            # Item 4 - QB(ML/MIN)
            if not (0 < row[columns_to_check[3]] <= 600):
                # print(f'\nQB Error : {row['MR NO']}, {row['Center Name']}, {row[columns_to_check[3]]}')
                error_list.append(row)

            # Check Item 5 - SP KT?V
            try:
                # Assuming the formula for SP Kt/V is already computed and stored in the cell
                sp_kt_v = float(row[columns_to_check[4]])
                if sp_kt_v == 0:
                    # print(f'\nSP Kt/V Error : {row["MR NO"]}, {row["Center Name"]}, {sp_kt_v}')
                    error_list.append(row)
            except ValueError:
                # print(f'\nSP Kt/V Error (Invalid Value) : {row["MR NO"]}, {row["Center Name"]}, {row[columns_to_check[4]]}')
                error_list.append(row)

            # Check Item 6 (URR)
            try:
                # Assuming the formula for URR is already computed and stored in the cell
                urr = float(row[columns_to_check[5]])
                if not (0 <= urr <= 100):
                    # print(f'\nURR Error : {row["MR NO"]}, {row["Center Name"]}, {urr}')
                    error_list.append(row)
            except ValueError:
                # print(f'\nURR Error (Invalid Value) : {row["MR NO"]}, {row["Center Name"]}, {row[columns_to_check[5]]}')
                error_list.append(row)

            # Check if 'MR NO' does not start with 'MR00'
            if not row['MR No.'].startswith('MR00'):
                print(f'\nMR NO Invalid: {row["MR NO"]}, {row["Center Name"]}')
                error_list.append(row)

    # Display the DataFrame containing rows with any blank values
    error_rows_df = pd.DataFrame(error_list, columns=df.columns)

    return error_rows_df



# From APAC transform to Insta like df
def monthly_Clinical_data(month):
    apac = read_apac_folders(convert_date(month))
    # Remove unwanted MR No
    apac = apac[~apac['MR No.'].isin(['TEAMMATE', 'NEW'])]

    # Select columns
    apac = apac[[
        'Patient ID  ',
        'MR No.',
        'Center Name', # Center Name
        'Reporting Month', # Reporting Month
        'Physician Responsible', # Physician Responsible
        '# of Txs per Week', # # of Txs per Week
        'PREU', # Pre BUN Level (mg/dL)
        'POSU', # Post BUN Level (mg/dL)
        'Draw Date', # Draw Date, BUN Draw Data
        'Pre Tx Weight (Kg)', # Pre Tx Weight (Kg)
        'Post Tx Weight (Kg)', # Post Tx Weight (Kg)
        'Tx Duration (mins)', # Tx Duration (mins)
        'SP Kt/V', # Sp Kt/V
        'Targe UF',
        'URR', # URR
        'HB', # Hgb (gm/dL)
        'ALB', # Alb (gm/dL)
        'PHOS', # Phos (mg/dL)
        'FERR', # Ferritin (mg/L)
        'Tsat', # Tsat %
        'CA', # Ca (mg/dL)
        'K', # K (mEq/L)
        'PTH', # PTH (pg/mL)
        'QB (mL/min)', # QB (mL/min),
        'Ref No', # Lab No
    ]]

    # total size
    total_length = len(apac)
    dupe_pt = apac['MR No.'].duplicated().sum()
    hb_notNull = len(apac[apac['HB'].notna()])

    print(f"\nTotal data size: {total_length}")
    print(f"Total duplicate: {dupe_pt}")
    print(f"Total HB not null: {hb_notNull}, {np.round(hb_notNull/total_length * 100, 1)}%")

    return apac

def sepResult(df):
    results_list = [
        'SP Kt/V',
        'HB', 
        'ALB',
        'PHOS',
        'FERR',
        'Tsat',
        'CA',
        'K',
        'PTH',
        'QB (mL/min)',
    ]
    
    separate_dfs = {}
    
    for col in results_list:
        if col in df.columns:  # Ensure the column exists in the DataFrame
            # Create a separate DataFrame with the current column and any identifying columns
            if col == 'SP Kt/V':
                separate_dfs[col] = df[[
                    'MR No.', 
                    col,
                    'PREU',
                    'POSU',
                    'Pre Tx Weight (Kg)',
                    'Post Tx Weight (Kg)',
                    'Tx Duration (mins)',
                    'Targe UF',
                    'URR', # URR
                    'Draw Date'
                    ]].dropna().reset_index(drop=True)
                
                # Rename Draw Date
                separate_dfs[col] = separate_dfs[col].rename({'Draw Date' : f'Draw Date_{col}'}, axis=1)
            else:
                separate_dfs[col] = df[['MR No.', col, 'Draw Date']].dropna().reset_index(drop=True)

                # Sort by Draw Date
                separate_dfs[col]  = separate_dfs[col] .sort_values(by=['MR No.', 'Draw Date'], ascending=[True, False])

                # Drop duplicate take the first row
                separate_dfs[col]  = separate_dfs[col] .drop_duplicates(subset=['MR No.'], keep='first')
                
                # Rename Draw Date
                separate_dfs[col] = separate_dfs[col].rename({'Draw Date' : f'Draw Date_{col}'}, axis=1)
        else:
            print(f"Warning: Column '{col}' not found in the DataFrame.")
    
    return separate_dfs



# Read Billing Report to get HD counts
def readBillingReport(month):
    folderpath = os.path.join(DATA_FOLDER, 'Billing Report')
    files = [file for file in os.listdir(folderpath) if file.startswith(f"{month} Billing Report") and file.endswith('.csv')]

    df = pd.read_csv(os.path.join(folderpath, files[0]), skiprows=2)

    # Filter item only HD
    df = df[df['Item Description'] == 'HAEMODIALYSIS']

    df = df.groupby('MR No.')['Bill No.'].count().reset_index(name="HD Count")

    return df



# Read Patient Details
def readPatientDetails(month):
    folderpath = os.path.join(DATA_FOLDER, 'Patient Details All Center')
    files = [file for file in os.listdir(folderpath) if file.startswith(f"{month} patient details") and file.endswith('.csv')]

    df = pd.read_csv(os.path.join(folderpath, files[0]), skiprows=1)

    # Last Visit Month
    df['Last Visit Month'] = pd.to_datetime(df['Last Visit Date'], dayfirst=True).dt.to_period('M')

    return df



# Merge Medical Outcomes into Active Patients data
def addIn_MedicalOutcomes(patientData, separate_dfs):

    for outcome, outcome_df in separate_dfs.items():
         # Merge activePatientData with the outcome DataFrame on 'MR NO' and 'Draw Date'
         patientData = patientData.merge(
            outcome_df,
            on=['MR No.'],
            how='left'
         )

    return patientData




def getDeathPtDetail(month):
     # Read Death Report
    folderpath = os.path.join(DATA_FOLDER, 'Death Report')
    files = [file for file in os.listdir(folderpath) if file.startswith(f"{month} Death Report") and file.endswith('.csv')]
    death_pt = pd.read_csv(os.path.join(folderpath, files[0]), skiprows=2)

    # Only keep the dead pt MR No.
    death_pt = death_pt[['MR No.']]

    death_pt['Mortality'] = 1

    return death_pt



# read Hospitalization Information
def readHospitalization(month):
    # Read Death Report
    folderpath = os.path.join(DATA_FOLDER, 'Hospitalizations')
    files = [file for file in os.listdir(folderpath) if file.startswith(f"{month} Hospitalization Information") and file.endswith('.csv')]
    hosp_info = pd.read_csv(os.path.join(folderpath, files[0]), skiprows=2)

    # Count the number of records for each MR No.
    pt_admission = hosp_info.groupby('MR No.')['Admission Date'].count().reset_index(name='Hospitalization')

    return pt_admission

# # Get Active patients
def getActivePt(month):
    pt_det = readPatientDetails(month)
    hd_count = readBillingReport(month)

    # Merge Patient Details with HD Count
    pt_det = pd.merge(pt_det, hd_count, on='MR No.', how='left')

    # Clean Patient Details. If Mortality = 1, skips the conditions
    df = pt_det[(pt_det['Last Visit Month'] == month) | (pt_det['HD Count'].notna())]

    # Filter
    df = df.loc[(df['Primary Center'] != 'DSSKL')]
    df = df.loc[(df['Discharge Type'].isna())]

    # Only keep MR No
    df = df[['MR No.']]

    # Add Active indicator
    df['Active'] = 1

    return df


# Get overall data
def overallData(month, separate_dfs):
    # Read necessary functions
    pt_det = readPatientDetails(month)
    hd_count = readBillingReport(month)
    death_pt = getDeathPtDetail(month)
    hospital_admission = readHospitalization(month)
    active_patient = getActivePt(month)

    # Merge Patient Details with HD Count
    pt_det = pd.merge(pt_det, hd_count, on='MR No.', how='left')

    # Merge Patient Details with Mortality and Hospital Admission
    pt_det = pd.merge(pt_det, death_pt, on='MR No.', how='left')
    pt_det = pd.merge(pt_det, hospital_admission, on='MR No.', how='left')

    # Merge Patient Details with Active Patient
    pt_det = pd.merge(pt_det, active_patient, on='MR No.', how='left')

    # Merge each medical outcomes with their dates in Patient Details
    df = addIn_MedicalOutcomes(pt_det, separate_dfs)

    # Clean Patient Details. If Mortality = 1, skips the conditions
    df = df.loc[(df['Primary Center'] != 'DSSKL') | (df['Mortality'] == 1) | df['Hospitalization'] > 0]
    df = df.loc[((df['Last Visit Month'] == month) | df['HD Count'].notna()) | (df['Mortality'] == 1) | df['Hospitalization'] > 0]
    df = df.loc[(df['Discharge Type'].isna()) | (df['Mortality'] == 1) | df['Hospitalization'] > 0]

    # Remove duplicate rows based on 'MR No.'
    df = df.drop_duplicates(subset='MR No.')



    # Print stats
    print(f"Total Unique Patient {month}: {len(df['MR No.'].unique())}")
    print(f"Total Active patient: {len(df[df['Active'] == 1])}")
    print(f"Total Mortality: {len(df[df['Mortality'] == 1])}")
    print(f"Total Hospital Admission: {df['Hospitalization'].sum()}")

    # Drop unnecessary columns
    df = df.drop([
        'Duplicate MR No.',
        'Date of Birth',
        'Age',
        'Gender',
        'National/Passport ID Type',
        'National/Passport ID [NRIC: ******-**-****][Police ID: RF/******][Army ID: T*******]',
        'Patient Category',
        'Virology Status Date',
        'Virology Status',
        'Blood Group',
        'PDPA Consent (Yes/No)',
        'Patient Sources',
         'Marital Status',
        'Mobile No.',
        'Occupation',
        'Dialysis Status',
        'Religion',
        'Address',
        'Created Date',
        'Discharge Type',
        'Death Date',
        'Death Time',
        'Death Reason',
        'Discharging Doctor',
        'Discharge Remarks',
        'Dead On Arrival',
        'Patient Referral Source Hospital'
        ], axis=1)

    return df
