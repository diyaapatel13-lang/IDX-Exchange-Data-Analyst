#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 20:38:53 2026

@author: diyaapatel
"""

from pathlib import Path
import pandas as pd

# Folder locations
project_folder = Path("/Users/diyaapatel/Desktop/IDX-Exchange-Internship-Data")
raw_folder = project_folder / "raw"
processed_folder = project_folder / "processed"

processed_folder.mkdir(exist_ok=True)

# Locate all available files
listing_files = sorted(raw_folder.glob("CRMLSListing*.csv"))
sold_files = sorted(raw_folder.glob("CRMLSSold*.csv"))

print("Listing files found:", len(listing_files))
print("Sold files found:", len(sold_files))


def combine_and_filter(files, dataset_name):
    dataframes = []

    for file in files:
        print("Reading:", file.name)
        dataframe = pd.read_csv(file, low_memory=False)
        dataframes.append(dataframe)

    combined = pd.concat(dataframes, ignore_index=True)

    print(f"{dataset_name} rows before filtering:", len(combined))

    if "PropertyType" not in combined.columns:
        raise KeyError(f"PropertyType was not found in the {dataset_name} files.")

    residential = combined[
        combined["PropertyType"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("residential")
    ].copy()

    print(f"{dataset_name} rows after filtering:", len(residential))

    return residential


# Combine and filter each dataset separately
listings_residential = combine_and_filter(listing_files, "Listing")
sold_residential = combine_and_filter(sold_files, "Sold")

# Save processed datasets
listing_output = processed_folder / "combined_listings_residential.csv"
sold_output = processed_folder / "combined_sold_residential.csv"

listings_residential.to_csv(listing_output, index=False)
sold_residential.to_csv(sold_output, index=False)

print("\nWeek 1 processing complete.")
print("Saved:", listing_output)
print("Saved:", sold_output)
