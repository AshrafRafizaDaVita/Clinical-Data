import pandas as pd
import numpy as np
import os
from config import DATA_FOLDER, REGION_LIST

# Read Lab Result
def readResult():
    folderpath = os.path.join(DATA_FOLDER, r'Lab Result\Patient Result')
    files = [file for file in os.listdir(folderpath) if file.startswith('Patient_Result') and file.endswith('.csv')]

    results_array = []

    if files:
        for file in files:
            # Read Patient Result
            result = pd.read_csv(os.path.join(folderpath, file))

            # find Master Patient
            date_filename = file.split('_')[2].split('.')[0]
            master_folder = os.path.join(DATA_FOLDER, r'Lab Result\Master Patient')
            master = [file for file in os.listdir(master_folder) if file.startswith("Master_Patient") and date_filename in file]
            if master:
                master_patient = pd.read_csv(os.path.join(master_folder, master[0]))

            # merge Master Patient in Patient Result
            df = pd.merge(result, master_patient, on='IC No', how='left')
            print(f"Total result with no name: {len(df[df['Name'].isna()])}")

        
            # Append merge data in results array
            results_array.append(df)

        df = pd.concat(results_array)

        df['Region'] = df['Center Code'].map(REGION_LIST)
    
    print(f"Total Center Code: {len(df['Center Code'].unique())}")
    print(f"Total Records with No Region: {len(df[df['Region'].isna()])}")

    # Center Code with no region
    noRegion_centerCode = df[df['Region'].isna()]['Center Code'].unique()
    if noRegion_centerCode:
        print(F"Center Code with No Region: {noRegion_centerCode}")

    # Center not available in data
    for key in REGION_LIST.keys():
        if key not in df['Center Code'].unique():
            print(f"\n{key} not in result")

    return df

# Count Lab Result for 