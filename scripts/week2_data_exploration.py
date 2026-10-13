#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 20:56:33 2026

@author: diyaapatel
"""

from pathlib import Path
import pandas as pd

# Folder locations
project_folder = Path("/Users/diyaapatel/Desktop/IDX-Exchange-Internship-Data")
processed_folder = project_folder / "processed"
outputs_folder = project_folder / "outputs"

outputs_folder.mkdir(exist_ok=True)

datasets = {
    "listings": processed_folder / "combined_listings_residential.csv",
    "sold": processed_folder / "combined_sold_residential.csv"
}

numeric_columns = ["ClosePrice", "LivingArea", "DaysOnMarket"]


def explore_dataset(dataset_name, file_path):
    print("\n" + "=" * 60)
    print(dataset_name.upper(), "DATASET")
    print("=" * 60)

    df = pd.read_csv(file_path, low_memory=False)

    # Basic dataset information
    print("\nShape:", df.shape)
    print("\nFirst five rows:")
    print(df.head())

    print("\nColumn data types:")
    print(df.dtypes.to_string())

    # Confirm property types
    if "PropertyType" in df.columns:
        print("\nUnique PropertyType values:")
        print(df["PropertyType"].value_counts(dropna=False))

    # Calculate missing-value percentages
    missing_percent = (
        df.isnull().mean().mul(100).sort_values(ascending=False)
    )

    missing_output = outputs_folder / f"{dataset_name}_missing_values.csv"
    missing_percent.to_csv(
        missing_output,
        header=["MissingPercent"]
    )

    print("\nColumns with more than 90% missing values:")
    high_missing = missing_percent[missing_percent > 90]

    if high_missing.empty:
        print("None")
    else:
        print(high_missing)

    # Generate statistics for required numeric columns
    available_columns = [
        column for column in numeric_columns if column in df.columns
    ]

    if available_columns:
        numeric_data = df[available_columns].apply(
            pd.to_numeric,
            errors="coerce"
        )

        statistics = numeric_data.describe().transpose()
        statistics_output = (
            outputs_folder / f"{dataset_name}_numeric_statistics.csv"
        )
        statistics.to_csv(statistics_output)

        print("\nNumeric statistics:")
        print(statistics)
        print("\nSaved:", statistics_output)
    else:
        print("\nNone of the required numeric columns were found.")

    print("Saved:", missing_output)


for name, path in datasets.items():
    explore_dataset(name, path)

print("\nWeek 2 data exploration complete.")
