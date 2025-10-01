"""
================================================================================
Data Corruption Utility (corrupt_data.py)
================================================================================

This utility script is designed for testing the data cleaning capabilities of the main
World Happiness Dashboard application (`app.py`). Its purpose is to take a clean,
complete CSV file and intentionally introduce missing values (NaNs) into specified
columns.

What this script does:
1.  Reads a source CSV file (defined in the CONFIGURATION section).
2.  For each column specified in `COLUMNS_TO_CORRUPT`, it randomly selects a
    percentage of rows (defined by `CORRUPTION_PERCENTAGE`).
3.  It replaces the existing values in these selected rows and columns with NaN,
    effectively "corrupting" the data.
4.  Saves the modified DataFrame to a new CSV file.

This allows for controlled testing of the "Missing Data Handling" feature in the
main application, ensuring it works correctly even on datasets that are initially clean.

To run:
Execute this script from the project's root directory:
$ python scripts/corrupt_data.py
================================================================================
"""
import pandas as pd
import numpy as np
import os

# --- CONFIGURATION ---
# Use this section to control the script's behavior.

# The name of the source CSV file located in the `data` directory.
SOURCE_FILENAME = 'WHR2024.csv'

# The name of the output file that will be saved in the `data` directory.
OUTPUT_FILENAME = 'WHR2024_with_missing.csv'

# A list of column names where missing values should be introduced.
# NOTE: The script will use standardized column names. It runs the same standardization
# function as the main app to ensure column names are found correctly.
COLUMNS_TO_CORRUPT = [
    'Social Support',
    'Life Expectancy',
    'Generosity'
]

# The percentage of rows to corrupt in each specified column (from 0.0 to 1.0).
# For example, 0.1 means 10% of the data will be removed.
CORRUPTION_PERCENTAGE = 0.1


# --- HELPER FUNCTION (copied from app.py for consistency) ---
def standardize_columns(dataframe):
    """
    Standardizes column names to ensure consistency with the main app.
    This allows `COLUMNS_TO_CORRUPT` to use clean names.
    """
    df_original = dataframe.copy()
    rename_map = {
        'Country': ['country'], 'Region': ['regional indicator'],
        'Happiness Score': ['happiness score', 'ladder score'], 'GDP per capita': ['gdp per capita'],
        'Social Support': ['social support'], 'Life Expectancy': ['healthy life expectancy'],
        'Freedom': ['freedom to make life choices'], 'Generosity': ['generosity'],
        'Corruption': ['perceptions of corruption']
    }
    df_clean = pd.DataFrame()
    processed_original_cols = set()
    for standard_name, keywords in rename_map.items():
        best_match_col = None
        for col_original in df_original.columns:
            if col_original in processed_original_cols: continue
            if col_original.lower().strip().startswith("explained by:"):
                col_clean = col_original.lower().replace('explained by: ', '').strip()
                if any(keyword in col_clean for keyword in keywords):
                    best_match_col = col_original
                    break
        if not best_match_col:
            for col_original in df_original.columns:
                if col_original in processed_original_cols: continue
                col_clean = col_original.lower().strip()
                if any(keyword in col_clean for keyword in keywords):
                    best_match_col = col_original
                    break
        if best_match_col:
            df_clean[standard_name] = df_original[best_match_col]
            processed_original_cols.add(best_match_col)
    for col in df_original.columns:
        if col not in processed_original_cols: df_clean[col] = df_original[col]
    return df_clean


# --- MAIN SCRIPT LOGIC ---
def corrupt_csv(source_path, output_path, columns_to_corrupt, percentage):
    """
    Reads a CSV, introduces NaN values, and saves it to a new file.
    """
    print(f"[*] Loading source file: {os.path.basename(source_path)}")
    if not os.path.exists(source_path):
        print(f"[!] ERROR: Source file not found at path: {source_path}")
        return

    df = pd.read_csv(source_path)

    # Standardize columns first to find the correct ones
    df_standardized = standardize_columns(df)

    print(f"[*] Starting data corruption process ({int(percentage * 100)}%)...")

    for col in columns_to_corrupt:
        if col in df_standardized.columns:
            # Calculate the number of values to remove
            n_to_remove = int(len(df_standardized) * percentage)

            # Get indices of rows that do not already have missing values in this column
            valid_indices = df_standardized[col].dropna().index

            if len(valid_indices) < n_to_remove:
                print(
                    f"[*] Warning: Not enough non-null data in column '{col}' to remove {n_to_remove} values. Removing {len(valid_indices)} instead.")
                n_to_remove = len(valid_indices)

            if n_to_remove == 0:
                print(f"    - No values to remove in column '{col}'. Skipping.")
                continue

            # Randomly choose indices to set to NaN
            indices_to_remove = np.random.choice(valid_indices, n_to_remove, replace=False)

            # Replace the values with NaN (Not a Number)
            df_standardized.loc[indices_to_remove, col] = np.nan
            print(f"    - In column '{col}', removed {n_to_remove} values.")
        else:
            print(f"[!] Warning: Column '{col}' not found in the standardized file. Skipping.")

    # Save the corrupted DataFrame to the output file
    df_standardized.to_csv(output_path, index=False)
    print("\n" + "=" * 50)
    print("              CORRUPTION COMPLETE")
    print("=" * 50)
    print(f"[*] Corrupted data saved to: {os.path.abspath(output_path)}")
    print("=" * 50)


if __name__ == "__main__":
    # Define paths relative to this script's location for robustness
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')

    source_file_path = os.path.join(DATA_DIR, SOURCE_FILENAME)
    output_file_path = os.path.join(DATA_DIR, OUTPUT_FILENAME)

    corrupt_csv(source_file_path, output_file_path, COLUMNS_TO_CORRUPT, CORRUPTION_PERCENTAGE)
