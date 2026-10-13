#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 21:01:08 2026

@author: diyaapatel
"""

from pathlib import Path
import pandas as pd

# Folder locations
project_folder = Path("/Users/diyaapatel/Desktop/IDX-Exchange-Internship-Data")
processed_folder = project_folder / "processed"
outputs_folder = project_folder / "outputs"

outputs_folder.mkdir(exist_ok=True)

# Download the official weekly 30-year mortgage-rate series from FRED
fred_url = (
    "https://fred.stlouisfed.org/graph/"
    "fredgraph.csv?id=MORTGAGE30US"
)

print("Downloading FRED mortgage-rate data...")

mortgage_rates = pd.read_csv(fred_url)

# Standardize the two column names
mortgage_rates.columns = ["Date", "MortgageRate"]

mortgage_rates["Date"] = pd.to_datetime(
    mortgage_rates["Date"],
    errors="coerce"
)

mortgage_rates["MortgageRate"] = pd.to_numeric(
    mortgage_rates["MortgageRate"],
    errors="coerce"
)

mortgage_rates = mortgage_rates.dropna(
    subset=["Date", "MortgageRate"]
)

# Convert weekly rates into monthly averages
mortgage_rates["MortgageMonth"] = (
    mortgage_rates["Date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_rates = (
    mortgage_rates
    .groupby("MortgageMonth", as_index=False)["MortgageRate"]
    .mean()
)

monthly_rates = monthly_rates.rename(
    columns={"MortgageRate": "MonthlyMortgageRate"}
)

monthly_output = outputs_folder / "monthly_mortgage_rates.csv"
monthly_rates.to_csv(monthly_output, index=False)

print("Monthly mortgage-rate observations:", len(monthly_rates))
print("Saved:", monthly_output)


def merge_mortgage_rates(
    input_file,
    date_column,
    output_file,
    dataset_name
):
    print("\nProcessing:", dataset_name)

    data = pd.read_csv(input_file, low_memory=False)

    if date_column not in data.columns:
        raise KeyError(
            f"{date_column} was not found in the {dataset_name} dataset."
        )

    data[date_column] = pd.to_datetime(
        data[date_column],
        errors="coerce"
    )

    data["MortgageMonth"] = (
        data[date_column]
        .dt.to_period("M")
        .astype(str)
    )

    merged_data = data.merge(
        monthly_rates,
        on="MortgageMonth",
        how="left"
    )

    valid_dates = merged_data[date_column].notna()

    missing_rates = merged_data.loc[
        valid_dates,
        "MonthlyMortgageRate"
    ].isna().sum()

    print("Rows:", len(merged_data))
    print("Invalid or missing dates:", (~valid_dates).sum())
    print("Valid dates missing a mortgage rate:", missing_rates)

    merged_data.to_csv(output_file, index=False)

    print("Saved:", output_file)


# Add rates to listings using ListingContractDate
merge_mortgage_rates(
    processed_folder / "combined_listings_residential.csv",
    "ListingContractDate",
    processed_folder / "listings_with_mortgage_rates.csv",
    "Listings"
)

# Add rates to sold properties using CloseDate
merge_mortgage_rates(
    processed_folder / "combined_sold_residential.csv",
    "CloseDate",
    processed_folder / "sold_with_mortgage_rates.csv",
    "Sold properties"
)

print("\nWeek 3 mortgage-rate merge complete.")
