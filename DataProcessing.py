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
    combined_df = combined_df.rename(columns={'MR NO(if teammate, tag as TEAMMATE, if new patient tag as NEW)': 'MR NO'})

    # Print unique Centers
    print(f"\nTotal Centers: {len(combined_df['Center Name'].unique())}")

    return combined_df



# Check for Blank Cells in APAC
def check_blanks(df):
    # Columns to check
    columns_to_check = [
        'MR NO', 
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
        if row['MR NO'] not in ['TEAMMATE', 'NEW']:
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
    df['MR NO'] = df['MR NO'].astype(str)

    # Iterate over each row
    for index, row in df.iterrows():
        # Check if any of the specified columns have blank values in the current row
        if row['MR NO'] not in ['TEAMMATE', 'NEW']:

            # Check Item 1 - PRE TX WEIGHT
            # if (row[columns_to_check[0]] < 30) & (row[columns_to_check[0]] > 200):
            if not ((30 <= row[columns_to_check[0]] <= 200)):
                print(f'\nPre Weight Invalid : {row['MR NO']}, {row['Center Name']}, {row[columns_to_check[0]]} Kg')
                error_list.append(row)

            # Check Item 2 - POST TX WEIGHT
            # if (row[columns_to_check[1]] < 30) & (row[columns_to_check[1]] > 200):
            if not (30 <= row[columns_to_check[1]] <= 200):
                print(f'\nPost Weight Invalid : {row['MR NO']}, {row['Center Name']}, {row[columns_to_check[1]]} Kg')
                error_list.append(row)

            # Item 3 - TARGET UF
            try:
                if ((row[columns_to_check[2]] <= 0) | (row[columns_to_check[2]] > 10)):
                    print(f'\nTarget UF Invalid : {row['MR NO']}, {row['Center Name']}, {row[columns_to_check[2]]}')
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
            if not row['MR NO'].startswith('MR00'):
                print(f'\nMR NO Invalid: {row["MR NO"]}, {row["Center Name"]}')
                error_list.append(row)

    # Display the DataFrame containing rows with any blank values
    error_rows_df = pd.DataFrame(error_list, columns=df.columns)

    return error_rows_df



# From APAC transform to Insta like df
def monthly_Clinical_data(month):
    apac = read_apac_folders(convert_date(month))
    # Remove unwanted MR No
    apac = apac[~apac['MR NO'].isin(['TEAMMATE', 'NEW'])]

    # Select columns
    apac = apac[[
        'Patient ID  ',
        'MR NO',
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
    dupe_pt = apac['MR NO'].duplicated().sum()
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
                    'MR NO', 
                    col,
                    'PREU',
                    'POSU',
                    'Post Tx Weight (Kg)', # Post Tx Weight (Kg)
                    'Tx Duration (mins)', # Tx Duration (mins)
                    'Targe UF',
                    'URR', # URR
                    'Draw Date'
                    ]].dropna().reset_index(drop=True)
            else:
                separate_dfs[col] = df[['MR NO', col, 'Draw Date']].dropna().reset_index(drop=True)

                # Sort by Draw Date
                separate_dfs[col]  = separate_dfs[col] .sort_values(by=['MR NO', 'Draw Date'], ascending=[True, False])

                # Drop duplicate take the first row
                separate_dfs[col]  = separate_dfs[col] .drop_duplicates(subset=['MR NO'], keep='first')
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



# Get Active Patients
def activePatients(month):
    pt_det = readPatientDetails(month)
    hd_count = readBillingReport(month)

    # Merge to get HD Count
    df = pd.merge(pt_det, hd_count, on='MR No.', how='left')

    # Clean Patient Details
    df = df[df['Primary Center'] != 'DSSKL']
    df = df[(df['Last Visit Month'] == month) | df['HD Count'].notna()]
    df = df[df['Discharge Type'].isna()]
    # df = df[df['Patient Category'] == 'General']

    # Print stats
    print(f"Total Unique Active Patient {month}: {len(df['MR No.'].unique())}")

    return df