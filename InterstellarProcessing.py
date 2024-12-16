import pandas as pd
import numpy as np
import os
from config import DATA_FOLDER, region_list_Insta

# Function to crrate table like in Interstellar tracker excel
def generate_transposed_table(df, required_columns):
    # Step 1: Transpose the DataFrame
    df_transpose = df.transpose()
    
    # Step 2: Set the first row as the new header and remove the old header
    df_transpose.columns = df_transpose.iloc[0]  # Set first row as column headers
    df_transpose = df_transpose.drop(df_transpose.index[0])  # Remove the row with headers
    
    # Step 3: Reindex with the required columns and fill missing columns with None
    df_transpose = df_transpose.reindex(columns=required_columns, fill_value=None)
    
    # Return the final transposed table
    return df_transpose

required_columns = [
    'SPS',
    'SPU',
    'Gurun',
    'Pendang',
    'Alor Setar',
    'Seberang Perai',
    'Kangar',
    'Sungai Siput',
    'Pekan Baru',
    'Region 1',

    'Batang Berjuntai',
    'Sabak Bernam',
    'Sungai Besar',
    'Tanjung Karang',
    'Bangi',
    'Kajang',
    'Cheras',
    'Puchong',
    'Jerantut',
    'Kota Warisan',
    'Region 2',

    'Kuala Pilah',
    'Seremban',
    'TTJ',
    'Rembau',
    'Wangsa Maju',
    'Sri Rampai',
    'Meru',
    'Andalas',
    'Region 3',

    'BBU',
    'Benut',
    'Kota Tinggi',
    'Pontian',
    'Batu Berendam',
    'Kuala Sungai Baru',
    'Johor Bharu',
    'Taman Seri Setia',
    'Masjid Tanah',
    'Region 4',

    'Kota Kinabalu',
    'Papar',
    'Sandakan',
    'Bangsar',
    'Tulip',
    'Rawang',
    'Antaragapi',
    'Tamansari',
    'Region 5',
    
    'Overall Country'
]


# MISSING LAB TEST
def missLab(df):

    missLab_df = df[[
        'MR No.',
        'HB', # If patient have HB result then the patient consider not missing # type: ignore
        'Primary Center',
        'Region',
        'Exclude From Interstellar',
        'Active',
    ]]

    # print(missLab_df[['HB']].info())

    #Conditions
    missLab_df = missLab_df[
        (missLab_df['Exclude From Interstellar'] == 'NO') & # Can comment this if to include the patients
        (missLab_df['Active'] == 1)]

    # df below is the patients who inside our range
    filtered_missLab_df = missLab_df[missLab_df['HB'].isnull()]


    ### --- MONTHLY MISSING LAB TEST --- ###
    # Country
    missLab_country = (filtered_missLab_df['MR No.'].count() / missLab_df['MR No.'].count() * 100).round(0)

    print(f"Total active patient: {missLab_df['MR No.'].count()}")
    print(f"Total patient who missed: {filtered_missLab_df['MR No.'].count()}")
    print(f"Overall country Missing lab test: {missLab_country}%")

    # # Region
    missLab_region = (filtered_missLab_df.groupby('Region')['MR No.'].count() / missLab_df.groupby('Region')['MR No.'].count() * 100).round(0)
    missLab_region

    # # Primary Center
    missLab_centre = (filtered_missLab_df.groupby(['Region','Primary Center'])['MR No.'].count() / missLab_df.groupby(['Region','Primary Center'])['MR No.'].count() * 100).round(0)
    missLab_centre

    # Combine all scores in one df for easier view
    # Create a DataFrame for country HB score
    missLab_country_df = pd.DataFrame({
        'Primary Center': ['Overall Country'],
        'Missing Lab Test': [missLab_country]
    })

    # Create a DataFrame for region HB scores
    missLab_region_df = missLab_region.reset_index(name='Missing Lab Test')
    missLab_region_df['Primary Center'] = missLab_region_df['Region']
    missLab_region_df = missLab_region_df.drop(columns='Region')

    # Create a DataFrame for center HB scores
    missLab_centre_df = missLab_centre.reset_index(name='Missing Lab Test')

    # Combine country, region, and center into a single DataFrame
    missLab_combined_df = pd.concat([missLab_country_df, missLab_region_df, missLab_centre_df], ignore_index=True)
    missLab_combined_df['Missing Lab Test'] = missLab_combined_df['Missing Lab Test'].fillna(0)
    missLab_combined_df

    # To generate table as in Interstellar Excel
    missLab_transpose = generate_transposed_table(missLab_combined_df[['Primary Center', 'Missing Lab Test']], required_columns)
    missLab_transpose

    return missLab_transpose


# HB 10-12 with EPO
def hb(df):

    hb_df = df[[
    'MR No.',
    'HB', # type: ignore
    'Primary Center',
    '>90days',
    'Region',
    'EPO Rate',
    'Exclude From Interstellar',
    'Active'
    ]]

    hb_df['HB'] = pd.to_numeric(hb_df['HB'], errors='coerce')

    #Conditions
    hb_df = hb_df[
        (hb_df['>90days'] == "YES") &
        (hb_df['EPO Rate'] > 0) &
        (hb_df['Exclude From Interstellar'] == 'NO') &
        (hb_df['Active'] == 1)]
    
    # df below is the patients who inside our range
    filtered_hb_df = hb_df[
        (hb_df['HB'].notna()) &  # Exclude non-numeric values and NaN
        (hb_df['HB'] >= 10) &  # Include numeric values >= 10
        (hb_df['HB'] <= 12) # Include numeric values <= 12
    ]

    ### --- MONTHLY HB --- ###
    # Country
    hb_country = (filtered_hb_df['HB'].count() / len(hb_df) * 100).round(0)

    print(f"Total active, >90days with EPO patient: {len(hb_df)}")
    print(f"Total patient who in range: {filtered_hb_df['HB'].count()}")
    print(f"Overall country HB score: {hb_country}%")

    # Region
    hb_region = (filtered_hb_df.groupby(['Region'])['HB'].count() / hb_df.groupby(['Region'])['HB'].count() * 100).round(0)
    
    # Primary Center
    hb_centre = (filtered_hb_df.groupby(['Region', 'Primary Center'])['HB'].count() / hb_df.groupby(['Region', 'Primary Center'])['HB'].count() * 100).round(0)
    

    # Combine all scores in one df for easier view
    # Create a DataFrame for country HB score
    hb_country_df = pd.DataFrame({
        'Primary Center': ['Overall Country'],
        'HB Score': [hb_country]
    })

    # Create a DataFrame for region HB scores
    hb_region_df = hb_region.reset_index(name='HB Score')
    hb_region_df['Primary Center'] = hb_region_df['Region']
    hb_region_df = hb_region_df.drop(columns='Region')

    # Create a DataFrame for center HB scores
    hb_centre_df = hb_centre.reset_index(name='HB Score')

    # Combine country, region, and center into a single DataFrame
    hb_combined_df = pd.concat([hb_country_df, hb_region_df, hb_centre_df], ignore_index=True)

    # To generate table as in Interstellar Excel
    hb_transpose = generate_transposed_table(hb_combined_df[['Primary Center', 'HB Score']], required_columns)
    
    return hb_transpose


# PHOS <= 1.7 mmol/L
def phos(df):

    phos_df = df[[
    'MR No.',
    'PHOS', # type: ignore
    'Primary Center',
    '>90days',
    'Region',
    'Exclude From Interstellar',
    'Active'
    ]]

    phos_df['PHOS'] = pd.to_numeric(phos_df['PHOS'], errors='coerce')

    #Conditions
    phos_df = phos_df[
        (phos_df['>90days'] == "YES") &
        (phos_df['Exclude From Interstellar'] == 'NO') &
        (phos_df['Active'] == 1)]
    
    # df below is the patients who inside our range
    filtered_phos_df = phos_df[
        (phos_df['PHOS'].notna()) &  # Exclude non-numeric values and NaN
        (phos_df['PHOS'] <= 1.7)
    ]

    ### --- MONTHLY --- ###
    # Country
    phos_country = (filtered_phos_df['MR No.'].count() / len(phos_df['MR No.']) * 100).round(0)

    print(f"Total active, >90days patient: {phos_df['MR No.'].count()}")
    print(f"Total patient who in range: {filtered_phos_df['MR No.'].count()}")
    print(f"Overall country HB score: {phos_country}%")

    # Region
    phos_region = (filtered_phos_df.groupby(['Region'])['MR No.'].count() / phos_df.groupby(['Region'])['MR No.'].count() * 100).round(0)
    
    # # Primary Center
    phos_centre = (filtered_phos_df.groupby(['Region', 'Primary Center'])['MR No.'].count() / phos_df.groupby(['Region', 'Primary Center'])['MR No.'].count() * 100).round(0)
    phos_centre

    # Combine all scores in one df for easier view
    # Create a DataFrame for country HB score
    phos_country_df = pd.DataFrame({
        'Primary Center': ['Overall Country'],
        'Phosphorus Score': [phos_country]
    })

    # Create a DataFrame for region HB scores
    phos_region_df = phos_region.reset_index(name='Phosphorus Score')
    phos_region_df['Primary Center'] = phos_region_df['Region']
    phos_region_df = phos_region_df.drop(columns='Region')

    # Create a DataFrame for center HB scores
    phos_centre_df = phos_centre.reset_index(name='Phosphorus Score')

    # Combine country, region, and center into a single DataFrame
    phos_combined_df = pd.concat([phos_country_df, phos_region_df, phos_centre_df], ignore_index=True)
    phos_combined_df

    # To generate table as in Interstellar Excel
    phos_transpose = generate_transposed_table(phos_combined_df[['Primary Center', 'Phosphorus Score']], required_columns)
    

    return phos_transpose


# IDWG <= 5%
def idwg(df):
    # dataDrop can be replace with other generated data
    idwg_df = df[[
        'MR No.',
        'IDH',
        'Primary Center',
        '>90days',
        'Region',
        'Exclude From Interstellar',
        'Active'
    ]]

    idwg_df['IDH'] = pd.to_numeric(idwg_df['IDH'], errors='coerce')

    #Conditions
    idwg_df = idwg_df[
        (idwg_df['>90days'] == "YES") &
        (idwg_df['Exclude From Interstellar'] == 'NO') &
        (idwg_df['Active'] == 1)]

    # df below is the patients who inside our range
    filtered_idwg_df = idwg_df[
        (idwg_df['IDH'].notna()) &  # Exclude non-numeric values and NaN
        (idwg_df['IDH'] <= 5)
    ]

    ### --- MONTHLY --- ###
    # Country
    idwg_country = (filtered_idwg_df['MR No.'].count() / idwg_df['MR No.'].count() * 100).round(0)

    print(f"Total active, >90days patient: {idwg_df['MR No.'].count()}")
    print(f"Total patient who in range: {filtered_idwg_df['MR No.'].count()}")
    print(f"Overall country HB score: {idwg_country}%")

    # Region
    idwg_region = (filtered_idwg_df.groupby(['Region'])['MR No.'].count() / idwg_df.groupby(['Region'])['MR No.'].count() * 100).round(0)
    idwg_region

    # # Primary Center
    idwg_centre = (filtered_idwg_df.groupby(['Region', 'Primary Center'])['MR No.'].count() / idwg_df.groupby(['Region', 'Primary Center'])['MR No.'].count() * 100).round(0)
    idwg_centre

    # Combine all scores in one df for easier view
    # Create a DataFrame for country HB score
    index_title = 'IDWG Score'
    idwg_country_df = pd.DataFrame({
        'Primary Center': ['Overall Country'],
        index_title: [idwg_country]
    })

    # Create a DataFrame for region HB scores
    idwg_region_df = idwg_region.reset_index(name=index_title)
    idwg_region_df['Primary Center'] = idwg_region_df['Region']
    idwg_region_df = idwg_region_df.drop(columns='Region')

    # Create a DataFrame for center HB scores
    idwg_centre_df = idwg_centre.reset_index(name=index_title)

    # Combine country, region, and center into a single DataFrame
    idwg_combined_df = pd.concat([idwg_country_df, idwg_region_df, idwg_centre_df], ignore_index=True)
    idwg_combined_df

    # To generate table as in Interstellar Excel
    idwg_transpose = generate_transposed_table(idwg_combined_df[['Primary Center', index_title]], required_columns)

    return idwg_transpose

# MORTALITY
def mortality(df):
    # dataDrop can be replace with other generated data
    mortality_df = df[[
        'MR No.',
        'Mortality',
        'Primary Center',
        'Region',
        'Active'
    ]]

    # Active patient df is used to get the patient count
    activePtCount_df = mortality_df[(mortality_df['Active'] == 1)]

    # df below is the patients who inside our range
    filtered_mortality_df = mortality_df[(mortality_df['Mortality'] == 1)]

    ### --- MONTHLY --- ###
    # Country
    mortality_country = (filtered_mortality_df['MR No.'].count() / activePtCount_df['MR No.'].count() * 100).round(1)

    print(f"Total active, >90days patient: {activePtCount_df['MR No.'].count()}")
    print(f"Total deaths: {filtered_mortality_df['MR No.'].count()}")
    print(f"Overall country mortality %: {mortality_country}%")

    # Region
    mortality_region = (filtered_mortality_df.groupby(['Region'])['MR No.'].count() / activePtCount_df.groupby(['Region'])['MR No.'].count() * 100).round(1)
    mortality_region

    # # Primary Center
    mortality_centre = (filtered_mortality_df.groupby(['Region', 'Primary Center'])['MR No.'].count() / activePtCount_df.groupby(['Region', 'Primary Center'])['MR No.'].count() * 100).round(1)
    mortality_centre

    # Combine all scores in one df for easier view
    # Create a DataFrame for country HB score
    index_title = 'Mortality Rate'
    mortality_country_df = pd.DataFrame({
        'Primary Center': ['Overall Country'],
        index_title: [mortality_country]
    })

    # Create a DataFrame for region HB scores
    mortality_region_df = mortality_region.reset_index(name=index_title)
    mortality_region_df['Primary Center'] = mortality_region_df['Region']
    mortality_region_df = mortality_region_df.drop(columns='Region')
    mortality_region_df[index_title] = mortality_region_df[index_title].fillna(0) # Fill 0 if rate got NaN

    # Create a DataFrame for center HB scores
    mortality_centre_df = mortality_centre.reset_index(name=index_title)
    mortality_centre_df[index_title] = mortality_centre_df[index_title].fillna(0) # Fill 0 if rate got NaN

    # Combine country, region, and center into a single DataFrame
    mortality_combined_df = pd.concat([mortality_country_df, mortality_region_df, mortality_centre_df], ignore_index=True)
    mortality_combined_df

    # To generate table as in Interstellar Excel
    mortality_transpose = generate_transposed_table(mortality_combined_df[['Primary Center', index_title]], required_columns)
    
    return mortality_transpose


# HOSPITALIZATION PER PATIENT PER YEAR
def hospitalizations(selectedMonth, df):

    # Previous 11 months admission
    folder_path = os.path.join(DATA_FOLDER, 'Eleven Months Hospitalizations')
    file = [file for file in os.listdir(folder_path) if file.startswith(f"{selectedMonth} Hospitalization Information") and file.endswith('.csv')]
    prev11mnths_hosp = pd.read_csv(os.path.join(folder_path, file[0]), skiprows=2)
    
    # Add Region in above df
    prev11mnths_hosp['Region'] = prev11mnths_hosp['Primary Center'].map(region_list_Insta)
    print(f"Total missing Region in prev dataset: {len(prev11mnths_hosp[prev11mnths_hosp['Region'].isna()])}")
    
    # dataDrop can be replace with other generated data
    hppy_df = df[[
        'MR No.',
        'Hospitalizations',
        'Primary Center',
        'Region',
        'Active'
    ]]

    # Active patient df is used to get the patient count
    activePtCount_df = hppy_df[(hppy_df['Active'] == 1)]

    # df below is the patients who inside our range
    filtered_hppy_df = hppy_df[(hppy_df['Hospitalizations'] > 0)]

    ### --- MONTHLY --- ###
    # Country
    centerPrev_hosp = prev11mnths_hosp.groupby(['Primary Center'])['MR No.'].count()
    hppy_country = ((filtered_hppy_df['MR No.'].count() + centerPrev_hosp.sum()) / activePtCount_df['MR No.'].count()).round(2)
    hosp_country = (filtered_hppy_df['MR No.'].count() / activePtCount_df['MR No.'].count() * 100).round(0) # Hosp %

    print(f"Total active, >90days patient: {activePtCount_df['MR No.'].count()}")
    print(f"Total current month HPPY: {filtered_hppy_df['MR No.'].count()}")
    print(f"Total previous 11 months HPPY: {centerPrev_hosp.sum()}")
    print(f"Overall country HPPY score: {hppy_country}")

    # Region
    region_current_adm_counts = filtered_hppy_df.groupby(['Region'])['MR No.'].count().reset_index(name='current_adm_counts')
    regionPrev_adm_counts = prev11mnths_hosp.groupby(['Region'])['MR No.'].count().reset_index(name='regionPrev_adm_count')

    region_adm = pd.merge(region_current_adm_counts, regionPrev_adm_counts, on='Region', how='left')

    # Fill NaN values with 0 (in case some regions are missing in one of the DataFrames)
    region_adm.fillna(0, inplace=True)

    # Sum the counts from both DataFrames
    region_adm['total_count'] = region_adm['current_adm_counts'] + region_adm['regionPrev_adm_count']

    hppy_region = pd.merge(region_adm, activePtCount_df.groupby(['Region'])['MR No.'].count().reset_index(name='Total Patient'), on='Region', how='left')
    hppy_region['HPPY'] = (hppy_region['total_count'] / hppy_region['Total Patient']).round(2)
    hppy_region['Hospitalizations %'] = (hppy_region['current_adm_counts'] / hppy_region['Total Patient']).round(2)

    # Center
    center_current_adm_counts = filtered_hppy_df.groupby(['Primary Center'])['MR No.'].count().reset_index(name='current_adm_counts')
    centerPrev_adm_counts = prev11mnths_hosp.groupby(['Primary Center'])['MR No.'].count().reset_index(name='centerPrev_adm_count')

    center_adm = pd.merge(center_current_adm_counts, centerPrev_adm_counts, on='Primary Center', how='outer')

    # Fill NaN values with 0 (in case some centers are missing in one of the DataFrames)
    center_adm.fillna(0, inplace=True)

    # Sum the counts from both DataFrames
    center_adm['total_count'] = center_adm['current_adm_counts'] + center_adm['centerPrev_adm_count']

    hppy_center = pd.merge(activePtCount_df.groupby(['Region','Primary Center'])['MR No.'].count().reset_index(name='Total Patient'), center_adm, on='Primary Center', how='left')
    hppy_center['HPPY'] = (hppy_center['total_count'] / hppy_center['Total Patient']).round(2)
    hppy_center['Hospitalizations %'] = (hppy_center['current_adm_counts'] / hppy_center['Total Patient']).round(2)
    
    # Combine all scores in one df for easier view
    # Create a DataFrame for country HB score
    index_title1 = 'HPPY'

    hppy_country_df = pd.DataFrame({
        'Primary Center': ['Overall Country'],
        index_title1: [hppy_country]
    })

    # Create a DataFrame for region HB scores
    hppy_region_df = hppy_region[['Region', 'HPPY']]
    # hppy_region_df.rename(columns={'index': index_title}, inplace=True)
    hppy_region_df['Primary Center'] = hppy_region_df['Region']
    hppy_region_df = hppy_region_df.drop(columns='Region')
    hppy_region_df

    # Create a DataFrame for center HB scores
    hppy_centre_df = hppy_center[['Primary Center', 'HPPY']]
    hppy_centre_df

    # Combine country, region, and center into a single DataFrame
    hppy_combined_df = pd.concat([hppy_country_df, hppy_region_df, hppy_centre_df], ignore_index=True)
    hppy_combined_df

    # To generate table as in Interstellar Excel
    hppy_transpose = generate_transposed_table(hppy_combined_df[['Primary Center', index_title1]], required_columns)
    
    # Combine all scores in one df for easier view
    # Create a DataFrame for country HB score
    index_title2 = 'Hospitalizations %'

    hosp_country_df = pd.DataFrame({
        'Primary Center': ['Overall Country'],
        index_title2: [hosp_country]
    })

    # Create a DataFrame for region HB scores
    hosp_region_df = hppy_region[['Region', index_title2]]
    # hppy_region_df.rename(columns={'index': index_title}, inplace=True)
    hosp_region_df['Primary Center'] = hosp_region_df['Region']
    hosp_region_df = hosp_region_df.drop(columns='Region')
    hosp_region_df

    # Create a DataFrame for center HB scores
    hosp_centre_df = hppy_center[['Primary Center', index_title2]]
    hosp_centre_df

    # Combine country, region, and center into a single DataFrame
    hosp_combined_df = pd.concat([hosp_country_df, hosp_region_df, hosp_centre_df], ignore_index=True)
    hosp_combined_df

    # To generate table as in Interstellar Excel
    hosp_transpose = generate_transposed_table(hosp_combined_df[['Primary Center', index_title2]], required_columns)

    return hppy_transpose, hosp_transpose


