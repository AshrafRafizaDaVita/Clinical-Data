import pandas as pd
import numpy as np
import os
from config import DATA_FOLDER, REGION_LIST
from DataProcessing import readPatientDetails

# Read Lab Result
def readResult(ptDetailMonth):

    # PATIENT DEATULS
    patient_details = readPatientDetails(ptDetailMonth)
    patient_details = patient_details[['MR No.', 'National/Passport ID [NRIC: ******-**-****][Police ID: RF/******][Army ID: T*******]']]
    patient_details = patient_details.rename({
        'National/Passport ID [NRIC: ******-**-****][Police ID: RF/******][Army ID: T*******]' : 'IC No'
    }, axis=1)
    patient_details['IC No'] = patient_details['IC No'].str.replace('-', '')


    # READ RESULT RAW DATA
    folderpath = os.path.join(DATA_FOLDER, r'Lab Result\Patient Result')
    files = [file for file in os.listdir(folderpath) if file.startswith('Patient_Result') and file.endswith('.csv')]

    results_array = []

    if files:
        for file in files:
            # Read Patient Result
            result = pd.read_csv(os.path.join(folderpath, file))
            result['IC No'] = result['IC No'].astype(str) # Ensure 'IC No' in both DataFrames is of type string
            # result['IC No'] = result['IC No'].astype(str).str.lstrip() # Remove leading whitespace

            # find Master Patient
            date_filename = file.split('_')[2].split('.')[0]
            master_folder = os.path.join(DATA_FOLDER, r'Lab Result\Master Patient')
            master = [file for file in os.listdir(master_folder) if file.startswith("Master_Patient") and date_filename in file]
            if master:
                master_patient = pd.read_csv(os.path.join(master_folder, master[0]))
                master_patient['IC No'] = master_patient['IC No'].astype(str) # Ensure 'IC No' in both DataFrames is of type string

            # merge Master Patient in Patient Result
            df = pd.merge(result, master_patient, on='IC No', how='left')
            print(f"Total result with no name for {date_filename}: {len(df[df['Name'].isna()])}")

        
            # Append merge data in results array
            results_array.append(df)

        df = pd.concat(results_array)

        df['Region'] = df['Center Code'].map(REGION_LIST)

        # Merge with Patient Details to get MR No.
        df = pd.merge(df, patient_details, on='IC No', how='left')

        # Change Date columns to datetime format. Add Month and Quarter
        df['Draw Date'] = pd.to_datetime(df['Draw Date'], dayfirst=True)
        df['Month'] = df['Draw Date'].dt.to_period('M')
        df['Quarter'] = df['Draw Date'].dt.to_period('Q')

    
    print(f"\nTotal data: {len(df)}")
    print(f"Total Center Code: {len(df['Center Code'].unique())}")
    print(f"Total Records with No Region: {len(df[df['Region'].isna()])}")
    print(f"Available Month: {", ".join(map(str, df['Month'].unique()))}")

    print(f"\nTotal missing MR No.: {len(df[df['MR No.'].isna()])}")

    # Center Code with no region
    noRegion_centerCode = df[df['Region'].isna()]['Center Code'].unique()
    if noRegion_centerCode:
        print(F"Center Code with No Region: {noRegion_centerCode}")

    # Center not available in data
    for key in REGION_LIST.keys():
        if key not in df['Center Code'].unique():
            print(f"\n{key} not in result")

    return df

# Create a df only for HB based on Month
# Each of MR No. will have 1 HB per month
def monthly_hb(df):
    # Select columns
    df = df[[
        'MR No.',
        'HB',
        'Draw Date',
        'Month',
        'Quarter'
    ]]

    # Remove null MR No.
    df = df[(df['MR No.'].notna()) & (df['HB'].notna())]

    # Define a helper function to calculate the distance from the range 10-12
    def hb_distance(hb):
        if 10 <= hb <= 12:
            return 0 # Ideal range
        elif hb < 10:
            return 10 - hb # Distance below 10
        else:
            return hb - 12 # Distance above 12
    
    # Add a column for HB distance to the ideal range
    df['HB_Distance'] = df['HB'].apply(hb_distance)

    # Sort by MR No., Month, and HB Distance (ascending)
    df = df.sort_values(by=['MR No.', 'Month', 'HB_Distance', 'Draw Date'])

    # Drop duplicates to keep the closest HB per Month for each MR No.
    df = df.drop_duplicates(subset=['MR No.', 'Month'], keep='first')

    # Drop the helper column
    df = df.drop(columns=['HB_Distance'])

    return df

# Create a df only for PHOS based on Month
# Each of MR No. will have 1 PHOS per month
def monthly_phos(df):
    # Select columns
    df = df[[
        'MR No.',
        'PHOS',
        'Draw Date',
        'Month',
        'Quarter'
    ]]

    # Remove null MR No.
    df = df[(df['MR No.'].notna()) & (df['PHOS'].notna())]

    # Sort the dataframe by 'MR No.', 'Quarter', and 'PHOS' (ascending order)
    df = df.sort_values(by=['MR No.', 'Quarter', 'PHOS'])

    # Drop duplicates by keeping the first entry for each MR No. and Quarter
    df = df.drop_duplicates(subset=['MR No.', 'Quarter'], keep='first')


    return df