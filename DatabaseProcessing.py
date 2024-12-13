import duckdb
import os
from config import DATA_FOLDER

# Path to directories
lab_result_dir = os.path.join(DATA_FOLDER, r'Lab Result\Patient Result')
master_patient_dir = os.path.join(DATA_FOLDER, r'Lab Result\Master Patient')

# Path to duckdb database
db_path = "patients_lab_result.duckdb"

# Connect to duckdb
con = duckdb.connect(db_path)

# Create a metadata table to track imported files (if not exists)
con.execute("""
    CREATE TABLE IF NOT EXISTS imported_files (
        filename TEXT PRIMARY KEY
    );
""")

def import_csv_files(folder_path, table_name):
    # Get the list of CSV files in folder
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

    for csv_file in csv_files:
        # Check if the file is already imported
        result = con.execute(
            "SELECT 1 FROM imported_files WHERE filename = ?", [csv_file]
        ).fetchone()

        if result:
            print(f"Skipping already imported file: {csv_file}")
            continue

        # import the CSV into duckdb
        file_path = os.path.join(folder_path, csv_file)
        con.execute(
            f"""
            CREATE OR REPLACE TABLE {table_name} AS
            SELECT * FROM read_csv_auto('{file_path}');
        """)
        print(f"Imported file into table '{table_name}': {csv_file}")

        # Add the file to the metadata table
        con.execute(
            "INSERT INTO imported_files (filename) VALUES (?)", [csv_file]
        )

# Import files from the respective directories into DuckDB tables
import_csv_files(lab_result_dir, "patient_result")
import_csv_files(master_patient_dir, "master_patient")

# Close the connection
con.close()