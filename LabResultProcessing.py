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
            df = pd.read_csv(os.path.join(folderpath, file))

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