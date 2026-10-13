#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 21:19:25 2026

@author: diyaapatel
"""

from pathlib import Path
import pandas as pd

# Folder locations
project_folder = Path("/Users/diyaapatel/Desktop/IDX-Exchange-Internship-Data")
processed_folder = project_folder / "processed"
outputs_folder = project_folder / "outputs"

outputs_folder.mkdir(exist_ok=True)

date_columns = [
    "ListingContractDate",
    "CloseDate",
    "OnMarketDate",
    "OffMarketDate",
    "PurchaseContractDate",
    "PendingTimestamp",
    "StatusChangeTimestamp"
]

numeric_columns = [
    "ListPrice",
    "OriginalListPrice",
    "ClosePrice",
    "LivingArea",
    "LotSizeSquareFeet",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "Latitude",
    "Longitude",
    "MonthlyMortgageRate"
]

positive_value_columns = [
    "ListPrice",
    "OriginalListPrice",
    "ClosePrice",
    "LivingArea"
]

nonnegative_columns = [
    "LotSizeSquareFeet",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket"
]

geography_columns = [
    "City",
    "CountyOrParish",
    "PostalCode",
    "Latitude",
    "Longitude"
]


def clean_and_validate(input_file, output_file, dataset_name):
    print("\n" + "=" * 60)
    print("Cleaning:", dataset_name)
    print("=" * 60)

    data = pd.read_csv(input_file, low_memory=False)
    print("Starting rows:", len(data))
    print("Starting columns:", len(data.columns))

    # Convert blank geographic values into missing values
    for column in geography_columns:
        if column in data.columns and data[column].dtype == "object":
            data[column] = data[column].replace(
                r"^\s*$",
                pd.NA,
                regex=True
            )

    # Clean date columns
    for column in date_columns:
        if column in data.columns:
            data[column] = pd.to_datetime(
                data[column],
                errors="coerce"
            )

    # Convert required numeric columns
    for column in numeric_columns:
        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )

    # Flag and remove invalid zero or negative values
    for column in positive_value_columns:
        if column in data.columns:
            flag_name = f"Invalid{column}Flag"

            data[flag_name] = (
                data[column].notna() &
                (data[column] <= 0)
            )

            data.loc[data[flag_name], column] = pd.NA

    # Flag and remove invalid negative values
    for column in nonnegative_columns:
        if column in data.columns:
            flag_name = f"Invalid{column}Flag"

            data[flag_name] = (
                data[column].notna() &
                (data[column] < 0)
            )

            data.loc[data[flag_name], column] = pd.NA

    # Timeline validation flags
    if {
        "CloseDate",
        "ListingContractDate"
    }.issubset(data.columns):
        data["CloseBeforeListingFlag"] = (
            data["CloseDate"].notna() &
            data["ListingContractDate"].notna() &
            (data["CloseDate"] < data["ListingContractDate"])
        )

    if {
        "PendingTimestamp",
        "ListingContractDate"
    }.issubset(data.columns):
        data["PendingBeforeListingFlag"] = (
            data["PendingTimestamp"].notna() &
            data["ListingContractDate"].notna() &
            (
                data["PendingTimestamp"] <
                data["ListingContractDate"]
            )
        )

    if {
        "OffMarketDate",
        "ListingContractDate"
    }.issubset(data.columns):
        data["OffMarketBeforeListingFlag"] = (
            data["OffMarketDate"].notna() &
            data["ListingContractDate"].notna() &
            (
                data["OffMarketDate"] <
                data["ListingContractDate"]
            )
        )

    # Geographic validation flags
    if {"Latitude", "Longitude"}.issubset(data.columns):
        data["MissingCoordinatesFlag"] = (
            data["Latitude"].isna() |
            data["Longitude"].isna()
        )

        data["InvalidCoordinatesFlag"] = (
            (
                data["Latitude"].notna() &
                ~data["Latitude"].between(-90, 90)
            ) |
            (
                data["Longitude"].notna() &
                ~data["Longitude"].between(-180, 180)
            )
        )

        # Approximate California coordinate boundaries
        data["OutsideCaliforniaFlag"] = (
            data["Latitude"].notna() &
            data["Longitude"].notna() &
            (
                ~data["Latitude"].between(32, 42) |
                ~data["Longitude"].between(-125, -113)
            )
        )

    # Flag records missing geographic information
    available_geography = [
        column
        for column in geography_columns
        if column in data.columns
    ]

    if available_geography:
        data["MissingGeographyFlag"] = (
            data[available_geography]
            .isna()
            .any(axis=1)
        )

    # Flag duplicated listing identifiers without deleting them
    identifier_column = None

    for possible_column in ["ListingKey", "ListingId"]:
        if possible_column in data.columns:
            identifier_column = possible_column
            break

    if identifier_column:
        data["DuplicateListingIdentifierFlag"] = (
            data[identifier_column]
            .duplicated(keep=False)
        )

    # Create a validation summary of every flag
    flag_columns = [
        column for column in data.columns
        if column.endswith("Flag")
    ]

    validation_summary = pd.DataFrame({
        "Flag": flag_columns,
        "FlaggedRows": [
            int(data[column].sum())
            for column in flag_columns
        ]
    })

    summary_file = (
        outputs_folder /
        f"{dataset_name}_validation_summary.csv"
    )

    validation_summary.to_csv(summary_file, index=False)
    data.to_csv(output_file, index=False)

    print("\nValidation summary:")
    print(validation_summary.to_string(index=False))
    print("\nFinal rows:", len(data))
    print("Saved cleaned data:", output_file)
    print("Saved validation summary:", summary_file)


clean_and_validate(
    processed_folder / "listings_with_mortgage_rates.csv",
    processed_folder / "listings_cleaned.csv",
    "listings"
)

clean_and_validate(
    processed_folder / "sold_with_mortgage_rates.csv",
    processed_folder / "sold_cleaned.csv",
    "sold"
)

print("\nWeek 4 cleaning and validation complete.")
