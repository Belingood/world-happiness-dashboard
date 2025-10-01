"""
================================================================================
Country Region Lookup Generator (create_lookup.py)
================================================================================

This script serves as a crucial pre-processing tool for the World Happiness Dashboard.
Its primary purpose is to create and maintain a master lookup file (`country_region_lookup.csv`)
which acts as a "single source of truth" for country names and their corresponding regions.

What this script does:
1.  Scans all `WHR*.csv` files in the `../data/` directory.
2.  Aggregates a unique, cleaned list of all country names found across all years.
3.  Builds a region dictionary by extracting region data from source files,
    prioritizing the most recent and complete files (as defined in `REGION_SOURCE_FILES`).
4.  Generates a `country_region_lookup.csv` file with two columns:
    - `canonical_name`: The clean, standardized name of the country.
    - `region`: The region, automatically filled where possible.
5.  Reports on its progress and explicitly lists any countries for which a region
    could not be found, prompting the user to fill them in manually.

This automated approach ensures data consistency, reproducibility, and makes the main
application (`app.py`) robust against inconsistencies in the source data.

To run:
Execute this script from the project's root directory:
$ python scripts/create_lookup.py
================================================================================
"""
import pandas as pd
import os

# --- CONFIGURATION ---
# Get the absolute path to the directory where this script is located (i.e., 'scripts')
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Build paths to the 'data' directory and the output file relative to the script's location
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'country_region_lookup.csv')

# Files to be scanned for region information, in order of priority (most reliable first)
REGION_SOURCE_FILES = ['WHR2024.csv', 'WHR2023.csv', 'WHR2022.csv']

def clean_country_name(name):
    """Removes asterisks and strips leading/trailing whitespace from a country name."""
    if isinstance(name, str):
        return name.replace('*', '').strip()
    return name

print("[*] Starting script to generate the country lookup file...")

# --- Step 1: Aggregate all unique and cleaned country names ---
all_countries = set()
print("\n[*] Step 1: Aggregating unique country names from all source files...")
if not os.path.isdir(DATA_DIR):
    print(f"[!] ERROR: Data directory not found at path: {os.path.abspath(DATA_DIR)}")
    print("[!] Please ensure the script is in a 'scripts' folder and the 'data' folder is at the same level.")
else:
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.csv') and filename.startswith('WHR'):
            print(f"    - Processing file: {filename}")
            try:
                df = pd.read_csv(os.path.join(DATA_DIR, filename))
                # Find the country column by checking for common names
                country_col = next((col for col in ['Country', 'Country name'] if col in df.columns), None)
                if country_col:
                    for country in df[country_col].dropna().unique():
                        all_countries.add(clean_country_name(country))
                else:
                     print(f"      [!] Warning: Country column not found in {filename}")
            except Exception as e:
                print(f"      [!] Error reading file {filename}: {e}")

# --- Step 2: Build a region dictionary from prioritized sources ---
region_lookup = {}
print("\n[*] Step 2: Extracting regions from source files...")
for filename in REGION_SOURCE_FILES:
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        print(f"    - Searching for regions in: {filename}")
        try:
            df = pd.read_csv(filepath)
            country_col = next((col for col in ['Country', 'Country name'] if col in df.columns), None)
            region_col = next((col for col in ['Regional indicator', 'Region'] if col in df.columns), None)

            if country_col and region_col:
                for index, row in df.iterrows():
                    country = clean_country_name(row[country_col])
                    region = row[region_col]
                    # Add the region only if this country hasn't been mapped yet
                    if country not in region_lookup and pd.notna(region):
                        region_lookup[country] = region
        except Exception as e:
            print(f"      [!] Error reading file {filename}: {e}")

# --- Step 3: Create and populate the final lookup DataFrame ---
print("\n[*] Step 3: Generating the final lookup file...")
sorted_countries = sorted(list(all_countries))
lookup_df = pd.DataFrame(sorted_countries, columns=['canonical_name'])

# Apply the created dictionary to auto-fill the 'region' column
lookup_df['region'] = lookup_df['canonical_name'].map(region_lookup)

# Save the result to a CSV file
lookup_df.to_csv(OUTPUT_FILE, index=False)

# --- Step 4: Report on the results ---
countries_with_region = lookup_df['region'].notna().sum()
countries_without_region = lookup_df['region'].isna().sum()
print("\n" + "="*50)
print("              GENERATION COMPLETE")
print("="*50)
print(f"[*] Lookup file saved to: {os.path.abspath(OUTPUT_FILE)}")
print(f"[*] Total unique countries found: {len(lookup_df)}")
print(f"[*] Regions automatically filled: {countries_with_region}")
print(f"[*] Regions requiring manual input: {countries_without_region}")

if countries_without_region > 0:
    missing_list = lookup_df[lookup_df['region'].isna()]['canonical_name'].tolist()
    print("\n[!] ACTION REQUIRED: Please open the lookup file and manually fill in the 'region' for the following countries:")
    for country in missing_list:
        print(f"    - {country}")
print("="*50)
