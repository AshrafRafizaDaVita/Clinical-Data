import pandas as pd
import numpy as np
import os
from config import APAC_DIRECTORIES, DATA_FOLDER, APAC_DIRECTORIES_C, region_list_Insta
from datetime import datetime
import shutil

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



# Copy generated APAC to shared folder
def copy_apac_to_sharefolder(sourceFolder):

    apac_dir = pd.read_excel(APAC_DIRECTORIES)
    apac_source_dir = fr"{APAC_DIRECTORIES_C}\{sourceFolder}"

    files = os.listdir(apac_source_dir)
    print(f"Total files: {len(files)}")

    for file_name in files:
        if os.path.isfile(os.path.join(apac_source_dir, file_name)):
            base_name = file_name.split('_')[2]
            destination_folder = apac_dir[apac_dir['Center'].str.contains(base_name, case=False, na=False)]['Link'].values
            if len(destination_folder) > 0:
                destination_folder = destination_folder[0]

            # Define the full source and destination file paths
            source_file_path = os.path.join(apac_source_dir, file_name)
            destination_file_path = os.path.join(destination_folder, file_name)

            print(source_file_path)
            print(destination_file_path)

            shutil.copy2(source_file_path, destination_file_path)
            print(f"Copied {file_name} to {destination_folder}")

        else:

            print(f"No matching folder found for {file_name}")


    return files



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
        'MR No.'
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
            if not ((29 <= row[columns_to_check[0]] <= 200)):
                print(f'\nPre Weight Invalid : {row['MR No.']}, {row['Center Name']}, {row[columns_to_check[0]]} Kg')
                error_list.append(row)

            # Check Item 2 - POST TX WEIGHT
            # if (row[columns_to_check[1]] < 30) & (row[columns_to_check[1]] > 200):
            if not (29 <= row[columns_to_check[1]] <= 200):
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
                print(f'\nMR NO Invalid: {row["MR No."]}, {row["Center Name"]}')
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
        'Pre Tx Weight (Kg)', # Pre Tx Weight (Kg)
        'Post Tx Weight (Kg)', # Post Tx Weight (Kg)
        'Tx Duration (mins)', # Tx Duration (mins)
        'SP Kt/V', # Sp Kt/V
        'Targe UF',
        'URR', # URR
        'HB', # Hgb (gm/dL)
        'Draw Date',
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

## Define result_list
results_list = [
        'Tx Details',
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

# Explode current month medical results
def sepResult(df):
    separate_dfs = {}
    
    for col in results_list:
        # Create a separate DataFrame with the current column and any identifying columns
        if col == 'Tx Details':
            separate_dfs[col] = df[[
                'MR No.',
                'Physician Responsible',
                '# of Txs per Week',
                'Pre Tx Weight (Kg)',
                'Post Tx Weight (Kg)',
                'Tx Duration (mins)',
                'Targe UF'
            ]]
        else:
            if (col in df.columns) & (col != 'Tx Details'):  # Ensure the column exists in the DataFrame
                if col == 'SP Kt/V':
                    separate_dfs[col] = df[[
                        'MR No.', 
                        col,
                        'PREU',
                        'POSU',
                        # 'Pre Tx Weight (Kg)',
                        # 'Post Tx Weight (Kg)',
                        # 'Tx Duration (mins)',
                        # 'Targe UF',
                        'URR', # URR
                        'Draw Date'
                        ]].dropna().reset_index(drop=True)
                    
                    # Rename Draw Date
                    separate_dfs[col] = separate_dfs[col].rename({'Draw Date' : f'BUN Draw Date'}, axis=1)
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
    pt_admission = hosp_info.groupby('MR No.')['Admission Date'].count().reset_index(name='Hospitalizations')

    return pt_admission


# Read Fluid Management Target Weight Report
def genIDWG(month):
    folderpath = os.path.join(DATA_FOLDER, 'Fluid Management Target Weight Report')
    files = [file for file in os.listdir(folderpath) if file.startswith(f"{month} Fluid Management Target Weight Report") and file.endswith('.xlsx')]
    idwg = pd.read_excel(os.path.join(folderpath, files[0]), skiprows=2)

    # filter rows where IDWG% is between MIN and MAX
    min = 0
    max = 10
    filtered_idwg = idwg[(idwg['IDWG%'] >= min) & (idwg['IDWG%'] <= max)]

    # group by MR NO and calculate the mean of IDWG%
    mean_idwg = filtered_idwg.groupby('MR NO')['IDWG%'].mean().reset_index()

    #initialize the output DF with all uniqaue MR NOs
    output_df = pd.DataFrame({
        'MR NO': idwg['MR NO'].unique()
    })

    # Merge with the grouped DF to ensure all MR NOs are included
    resultIdwg_df = pd.merge(output_df, mean_idwg, on='MR NO', how='left')

    # Fill NaN values for MR NOs with no IDWG% in the range
    resultIdwg_df['IDWG%'] = resultIdwg_df['IDWG%'].fillna(np.nan)
    resultIdwg_df['IDWG%'] = round(resultIdwg_df['IDWG%'],2)

    # Rename column to IDH
    resultIdwg_df = resultIdwg_df.rename({'MR NO': 'MR No.','IDWG%' : 'IDH'}, axis=1)

    return resultIdwg_df


# Get EPO from Sales Report
def getEPO(month):
    folderpath = os.path.join(DATA_FOLDER, 'Sales Report')
    files = [file for file in os.listdir(folderpath) if file.startswith(f"{month} DVA_Sales Report") and file.endswith('.xlsx')]
    
    # Create an empty df to concat all sheets
    sales_df = pd.DataFrame()

    # Read all sheets and concat them in sales_df
    with pd.ExcelFile(os.path.join(folderpath, files[0])) as xls:
        for sheet_name in xls.sheet_names:
            print(f"Reading sheet: {sheet_name}")
            sheet_df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=5)

            # Remove Grand total row
            sheet_df = sheet_df[sheet_df['Centre'] != 'Grand Total']

            # Change MRN colname to Code
            if 'MRN' in sheet_df.columns:
                sheet_df = sheet_df.rename({'MRN':'Code'}, axis=1)

            # Only select for EPO rows
            sheet_df = sheet_df[sheet_df['Product'].str.contains('EPO', case=False, na=False)]

            # Only select for End Of Month transaction
            sheet_df = sheet_df[sheet_df['Date'].dt.is_month_end ]
            
            print(f"Sheet {sheet_name} size: {len(sheet_df)}")
            sales_df = pd.concat([sales_df, sheet_df], ignore_index=True)

        print(f"Total accumulated size: {len(sales_df)}")

    epo_df = sales_df.groupby('Code')['Quantity'].sum().reset_index()
    epo_df = epo_df.rename({
        'Code':'MR No.',
        'Quantity':'EPO Rate'
    }, axis=1)

    return epo_df


# Get Primary Access
def getCVCPatient(month):
    folderpath = os.path.join(DATA_FOLDER, 'Access')
    files = [file for file in os.listdir(folderpath) if file.startswith(f"{month}-CVC-TRACKER") and file.endswith('.xlsx')]
    cvc_patient = pd.read_excel(os.path.join(folderpath, files[0]), sheet_name='Raw Data')

    return cvc_patient


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



# Get Patient to remove from Interstellar
def excludePatient(month):
    folderpath = os.path.join(DATA_FOLDER, 'Patient Exclude')
    files = [file for file in os.listdir(folderpath) if file.startswith(f"{month} Patient to remove") and file.endswith('.xlsx')]
    excludePtList = pd.read_excel(os.path.join(folderpath, files[0]))

    return excludePtList



# Read available Medical Outcomes (usually previous months)
def available_MO():
    # Read Death Report
    folderpath = os.path.join(DATA_FOLDER, 'Medical Outcomes Excel')
    files = [file for file in os.listdir(folderpath) if "Medical Outcomes" in file and file.endswith('.xlsx')]
    
    # Rename cols
    col_newname = {
        'Sp Kt/V' : 'SP Kt/V',
        'Hgb (gm/dL)' : 'HB',
        'Alb (gm/dL)': 'ALB',
        'Phos (mg/dL)' : 'PHOS',
        'Ferritin (mg/L)' : 'FERR',
        'Tsat %' : 'Tsat',
        'Ca (mg/dL)' : 'CA',
        'K (mEq/L)' : 'K',
        'PTH (pg/mL)' : 'PTH'
    }

    mo_array = []
    
    if files:
        for file in files:
            df = pd.read_excel(os.path.join(folderpath, file))

            # Based on Report Date get Quarter
            df['Report Date'] = pd.to_datetime(df['Report Date'], dayfirst=True, errors='coerce')

            # Check for invalid dates and handle them
            if df['Report Date'].isnull().any():
                print("Invalid dates found. Please check the data.")
            
            # Convert 'Report Date' to period (quarter)
            df['Report Quarter'] = df['Report Date'].dt.to_period('Q')

            # Rename columns if they exist in the DataFrame
            df = df.rename(columns={key: col_newname[key] for key in col_newname if key in df.columns})

            mo_array.append(df)

    mo = pd.concat(mo_array)

    # Rename columns
    mo = mo.rename({
        'Pre BUN Level (mg/dL)' : 'PREU',
        'Post BUN Level (mg/dL)' : 'POSU'
    }, axis=1)

    # Select necessary columns
    mo = mo[[
        'MR No.',
        'PREU', 
        'POSU', 
        'BUN Draw Date',
        'SP Kt/V', 
        'URR', 
        'HB', 
        'Draw Date_HB', 
        'ALB',
        'Draw Date_ALB', 
        'PHOS', 
        'Draw Date_PHOS', 
        'FERR', 
        'Draw Date_FERR', 
        'Tsat',
        'Draw Date_Tsat', 
        'CA', 
        'Draw Date_CA', 
        'K', 
        'Draw Date_K', 
        'PTH',
        'Draw Date_PTH',
        'Report Date' ,
        'Report Quarter'
    ]]

    return mo


# More than 90 days
def more90D(df):

    # Convert 'First Dialysis Date in Davita' to datetime and format as dd-mm-yyyy
    df['First Dialysis Date in Davita'] = pd.to_datetime(df['First Dialysis Date in Davita'], format='%d-%m-%Y', errors='coerce')

    # Calculate the difference in days between 'Report Date' and 'First Dialysis Date in Davita'
    df['days_diff'] = (df['Report Date'] - df['First Dialysis Date in Davita']).dt.days

    # Create '>90days' column with 'YES' if days_diff is greater than 90, otherwise 'NO'
    df['>90days'] = np.where(df['days_diff'] > 90, 'YES', 'NO')

    print(f"Total >90 Days Patient: {len(df[(df['>90days'] == 'YES') & (df['Primary'] == 'IJVC')])}")

    return df


# Get overall data
def overallData(month, separate_dfs):
    # Read necessary functions
    pt_det = readPatientDetails(month)
    hd_count = readBillingReport(month)
    death_pt = getDeathPtDetail(month)
    hospital_admission = readHospitalization(month)
    active_patient = getActivePt(month)
    idwg = genIDWG(month)
    epoCount = getEPO(month)
    cvcPatient = getCVCPatient(month)
    exludedPatient = excludePatient(month)

    # Merge Patient Details with HD Count
    pt_det = pd.merge(pt_det, hd_count, on='MR No.', how='left')

    # Merge Patient Details with EPO Count
    pt_det = pd.merge(pt_det, epoCount, on='MR No.', how='left')
    pt_det['EPO Rate'] = pt_det['EPO Rate'].fillna(0)

    # Add Primary Access
    pt_det['Primary'] = np.where((pt_det['MR No.'].isin(cvcPatient['MR Number'])),'IJVC','Arteriovenous fistula')

    # Add Exlude From Interstellar
    pt_det['Exclude From Interstellar'] = pt_det['MR No.'].apply(lambda x: 'YES' if x in exludedPatient['Patient Id'].values else 'NO')


    # Merge each medical outcomes with their dates in Patient Details
    pt_det = addIn_MedicalOutcomes(pt_det, separate_dfs)

    # Merge Patient Details with Mortality and Hospital Admission
    pt_det = pd.merge(pt_det, death_pt, on='MR No.', how='left')
    pt_det = pd.merge(pt_det, hospital_admission, on='MR No.', how='left')

    # Merge Patient Details with IDWG
    pt_det = pd.merge(pt_det, idwg, on='MR No.', how='left')

    # Merge Patient Details with Active Patient
    df = pd.merge(pt_det, active_patient, on='MR No.', how='left')

    # Clean Patient Details. If Mortality = 1, skips the conditions
    df = df.loc[(df['Primary Center'] != 'DSSKL') | (df['Mortality'] == 1) | df['Hospitalizations'] > 0]
    df = df.loc[((df['Last Visit Month'] == month) | df['HD Count'].notna()) | (df['Mortality'] == 1) | df['Hospitalizations'] > 0]
    df = df.loc[(df['Discharge Type'].isna()) | (df['Mortality'] == 1) | df['Hospitalizations'] > 0]

    # Remove duplicate rows based on 'MR No.'
    df = df.drop_duplicates(subset='MR No.')

    # Add Report Date and  Quarter column
    df['Report Date'] = pd.to_datetime(month + "-01")
    df['Report Month'] = df['Report Date'].dt.to_period('M')
    df['Report Quarter'] = df['Report Date'].dt.to_period('Q')

    # >90days
    df = more90D(df)

    # Add Region column based on Primary Center
    df['Region'] = df['Primary Center'].map(region_list_Insta)

    # Fill Na
    df.fillna({
        'Mortality': 0, 
        'Hospitalizations': 0,
        'Active' : 0,
        }, inplace=True)

    # Print stats
    print(f"Total Unique Patient {month}: {len(df['MR No.'].unique())}")
    print(f"Total Active patient: {len(df[df['Active'] == 1])}")
    print(f"Total Mortality: {len(df[df['Mortality'] == 1])}")
    print(f"Total Hospital Admission: {df['Hospitalizations'].sum()}")

    # Drop unnecessary columns
    df = df.drop([
        'Duplicate MR No.',
        'Date of Birth',
        'Age',
        'Gender',
        'National/Passport ID Type',
        # 'National/Passport ID [NRIC: ******-**-****][Police ID: RF/******][Army ID: T*******]',
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

# Logic: If 'ALB' is NaN, copy 'ALB_Quarter' and 'Draw Date_ALB_Quarter' if conditions are met
# Function to update a specific column
def update_column(df, col):
    # Check for missing values and update
    if col == 'SP Kt/V': # If SP Kt/V is null but the Quarter values is present
        condition = df[col].isna() & df[f'{col}_Quarter'].notna() & df['PREU_Quarter'].notna() & df['POSU_Quarter'].notna() & df['BUN Draw Date_Quarter'].notna() & df['URR_Quarter'].notna()
        df.loc[condition, col] = df.loc[condition, f'{col}_Quarter']
        df.loc[condition, 'PREU'] = df.loc[condition, 'PREU_Quarter']
        df.loc[condition, 'POSU'] = df.loc[condition, 'POSU_Quarter']
        df.loc[condition, 'BUN Draw Date'] = df.loc[condition, 'BUN Draw Date_Quarter']
        df.loc[condition, 'URR'] = df.loc[condition, 'URR_Quarter']
    else:
        condition = df[col].isna() & df[f'{col}_Quarter'].notna() & df[f'Draw Date_{col}_Quarter'].notna()
        df.loc[condition, col] = df.loc[condition, f'{col}_Quarter']
        df.loc[condition, f'Draw Date_{col}'] = df.loc[condition, f'Draw Date_{col}_Quarter']

    return df


# Insert previous result if null
def replaceNullResult(df):
    # Load all Medical Outcomes
    quarter_df = available_MO()

    # Merge with current month data
    df = pd.merge(df, quarter_df, on=['MR No.', 'Report Quarter'], how='left', suffixes=('', '_Quarter'))

    # List of columns that needs replacement if null
    col_list = [
        'SP Kt/V',
        'ALB',
        'PHOS',
        'FERR',
        'Tsat',
        'CA',
        'K',
        'PTH'
    ]

    # Update each column
    for col in col_list:
        df = update_column(df, col)
    
    # Drop columns with suffix '_Quarter'
    df = df.loc[:, ~df.columns.str.endswith('_Quarter')]

    return df


# Update HB
def update_hb(masterData, hb_data):
    # Merge hb_data into masterData
    df = pd.merge(masterData, hb_data, left_on=['MR No.', 'Report Month'], right_on=['MR No.', 'Month'], how='left', suffixes=('', '_Monthly_HB'))

    # Rename Draw Date to Draw Date_Monthly_HB
    df = df.rename(columns={'Draw Date': 'Draw Date_Monthly_HB'})

    # Define a helper function to choose the HB closest to 10–12
    def select_hb(row):
        if pd.isna(row['HB']) and not pd.isna(row['HB_Monthly_HB']):
            # First scenario: HB is null but HB_Monthly_HB is not null
            return row['HB_Monthly_HB'], row['Draw Date_Monthly_HB']
        
        elif not pd.isna(row['HB']) and not pd.isna(row['HB_Monthly_HB']):
            # Second scenario: Both HB and HB_Monthly_HB are not null
            hb_distance = abs(row['HB'] - 11)  # Distance of HB from the midpoint 11
            hb_monthly_distance = abs(row['HB_Monthly_HB'] - 11)  # Same for HB_Monthly_HB
            if hb_distance <= hb_monthly_distance:
                return row['HB'], row['Draw Date_HB']
            else:
                return row['HB_Monthly_HB'], row['Draw Date_Monthly_HB']
        else:
            # If HB is not null and HB_Monthly_HB is null or both are null, keep HB
            return row['HB'], row['Draw Date_HB']
    
    # Apply the helper function row-wise to determine Select_HB
    df[['Selected_HB', 'Selected_HB_Draw Date']] = df.apply(select_hb, axis=1, result_type="expand")

    return df

# Update PHOS
def update_phos(masterData, phos_data):
    # Merge phos_data into masterData
    df = pd.merge(masterData, phos_data, left_on=['MR No.', 'Report Quarter'], right_on=['MR No.', 'Quarter'], how='left', suffixes=('', '_Quarterly_PHOS'))

    # # Rename Draw Date to Draw Date_Quarterly_PHOS
    df = df.rename(columns={'Draw Date': 'Draw Date_Quarterly_PHOS'})

    # Define a helper function to choose the HB closest to 10–12
    def select_phos(row):
        if pd.isna(row['PHOS']) and not pd.isna(row['PHOS_Quarterly_PHOS']):
            # First scenario: PHOS is null but PHOS_Monthly_HB is not null
            return row['PHOS_Quarterly_PHOS'], row['Draw Date_Quarterly_PHOS']
        
        elif not pd.isna(row['PHOS']) and not pd.isna(row['PHOS_Quarterly_PHOS']):
            # Second scenario: Both PHOS and PHOS_Quarterly_PHOS are not null
            if row['PHOS'] <= row['PHOS_Quarterly_PHOS']:
                return row['PHOS'], row['Draw Date_PHOS']
            else:
                return row['PHOS_Quarterly_PHOS'], row['Draw Date_Quarterly_PHOS']
        else:
            # If HB is not null and HB_Monthly_HB is null or both are null, keep HB
            return row['PHOS'], row['Draw Date_PHOS']
    
    # Apply the helper function row-wise to determine Select_HB
    df[['Selected_PHOS', 'Selected_PHOS_Draw Date']] = df.apply(select_phos, axis=1, result_type="expand")

    return df

# Generate International Data Drop Excel
def gene_DataDrop(df):
    # Add columns
    df['Secondary'] = np.nan
    df['Location1'] = np.nan
    df['Organism1'] = np.nan
    df['Location2'] = np.nan
    df['Organism2'] = np.nan

    colDropList = [
        'HB',
        'Draw Date_HB',
        'PHOS',
        'Draw Date_PHOS'
    ]

    for col in colDropList:
        if col in df.columns:
            df.drop(col, axis=1, inplace=True)

    # Rename cols
    df = df.rename({
        'Selected_HB': 'HB',
        'Selected_HB_Draw Date': 'Draw Date_HB',

        'Selected_PHOS' : 'PHOS',
        'Selected_PHOS_Draw Date' : 'Draw Date_PHOS',
    }, axis=1)

    # Convert to numeric
    df['HB'] = pd.to_numeric(df['HB'], errors='coerce')


    col_list = [
        'MR No.',
        'Patient Name W/O Title',
        'National/Passport ID [NRIC: ******-**-****][Police ID: RF/******][Army ID: T*******]',
        'Primary Center',
        'First Dialysis Date(FDODD)',
        'First Dialysis Date in Davita',
        'Physician Responsible',
        '# of Txs per Week',
        'PREU',
        'POSU',
        'BUN Draw Date',
        'Pre Tx Weight (Kg)',
        'Post Tx Weight (Kg)',
        'IDH',
        'Tx Duration (mins)',
        'SP Kt/V',
        'URR',
        'HB',
        'Draw Date_HB',
        'ALB',
        'Draw Date_ALB',
        'PHOS',
        'Draw Date_PHOS',
        'FERR',
        'Draw Date_FERR',
        'Tsat',
        'Draw Date_Tsat',
        'CA',
        'Draw Date_CA',
        'K',
        'Draw Date_K',
        'PTH',
        'Draw Date_PTH',
        'QB (mL/min)',
        'Draw Date_QB (mL/min)',
        'Primary',
        'Secondary',
        'Location1',
        'Organism1',
        'Location2',
        'Organism2',
        'Report Date',
        '>90days',
        'EPO Rate',
        'Exclude From Interstellar',
        'Active',
        'Mortality',
        'Hospitalizations',
        'Region' 
    ]

    # Display column that not available in data
    for col in col_list:
        if col not in df.columns:
            print(F"{col} not found in data!")

    df = df[col_list]

    return df


## PHOS not achive
def PHOS_notInTarget(df, output_path):
    df = df[[
        'MR No.',
        'Patient Name W/O Title',
        'National/Passport ID [NRIC: ******-**-****][Police ID: RF/******][Army ID: T*******]',
        'Primary Center',
        'First Dialysis Date in Davita',
        'PHOS',
        'Draw Date_PHOS',
        'Region',
        '>90days'
    ]]

    df['First Dialysis Date in Davita'] = df['First Dialysis Date in Davita'].dt.strftime("%d/%m/%Y")
    df['Draw Date_PHOS'] = df['Draw Date_PHOS'].dt.strftime("%d/%m/%Y")

    # Filter row where PHOS >=1.7 and put ranking
    df = df[df['PHOS'] > 1.7]
    df['PHOS_Ranking'] = df['PHOS'] - 1.7

    # Sort tables
    df = df.sort_values(by=['Region', 'Primary Center', 'PHOS_Ranking'], ascending=[True, True, True])

    # Create Excel
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Overview', index=False)

        # Loop thru Primary Center
        for center, center_df in df.groupby('Primary Center'):
            center_df = center_df.drop([
                'First Dialysis Date in Davita',
                'Region',
                'PHOS_Ranking'
            ], axis=1)
            center_df.to_excel(writer, sheet_name=str(center), index=False)

    return df

