#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 18:42:29 2026

@author: diyaapatel
"""

from pathlib import Path
import gc
import pandas as pd
import numpy as np

# ---------------------------------------------------------
# Project folders
# ---------------------------------------------------------
BASE_DIR = Path("/Users/diyaapatel/Desktop/IDX-Exchange-Internship-Data")
PROCESSED_DIR = BASE_DIR / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)


def safe_ratio(numerator, denominator):
    """Calculate a ratio only when both values are valid and positive."""
    return np.where(
        numerator.notna() &
        denominator.notna() &
        (denominator > 0),
        numerator / denominator,
        np.nan
    )


def create_school_district_field(df):
    """
    Combine available MLS school-district fields without inventing values.
    A future geographic boundary file can replace missing district values.
    """
    district_columns = [
        column for column in [
            "HighSchoolDistrict",
            "MiddleOrJuniorSchoolDistrict",
            "ElementarySchoolDistrict"
        ]
        if column in df.columns
    ]

    if district_columns:
        df["SchoolDistrict"] = df[district_columns[0]]

        for column in district_columns[1:]:
            df["SchoolDistrict"] = (
                df["SchoolDistrict"].fillna(df[column])
            )
    else:
        df["SchoolDistrict"] = pd.NA

    return df


def save_grouped_summary(
    df,
    group_column,
    price_column,
    output_name
):
    """Create a grouped market summary when required fields exist."""

    if group_column not in df.columns:
        print(f"Skipped missing grouping column: {group_column}")
        return

    if price_column not in df.columns:
        print(f"Skipped missing price column: {price_column}")
        return

    summary = (
        df.dropna(subset=[group_column, price_column])
        .groupby(group_column)
        .agg(
            PropertyCount=(price_column, "count"),
            AveragePrice=(price_column, "mean"),
            MedianPrice=(price_column, "median")
        )
        .sort_values("MedianPrice", ascending=False)
        .reset_index()
    )

    if "DaysOnMarket" in df.columns:
        dom_summary = (
            df.dropna(subset=[group_column])
            .groupby(group_column)["DaysOnMarket"]
            .median()
            .rename("MedianDaysOnMarket")
            .reset_index()
        )

        summary = summary.merge(
            dom_summary,
            on=group_column,
            how="left"
        )

    summary.to_csv(
        OUTPUT_DIR / output_name,
        index=False
    )


# =========================================================
# SOLD PROPERTY FEATURE ENGINEERING
# =========================================================
sold_file = PROCESSED_DIR / "sold_cleaned.csv"

if sold_file.exists():
    print("Loading cleaned sold-property data...")
    sold = pd.read_csv(sold_file, low_memory=False)

    numeric_columns = [
        "ClosePrice",
        "ListPrice",
        "OriginalListPrice",
        "LivingArea",
        "DaysOnMarket"
    ]

    for column in numeric_columns:
        if column in sold.columns:
            sold[column] = pd.to_numeric(
                sold[column],
                errors="coerce"
            )

    # Price ratios
    if {"ClosePrice", "OriginalListPrice"}.issubset(sold.columns):
        sold["CloseToOriginalListPriceRatio"] = safe_ratio(
            sold["ClosePrice"],
            sold["OriginalListPrice"]
        )

    if {"ClosePrice", "ListPrice"}.issubset(sold.columns):
        sold["CloseToListPriceRatio"] = safe_ratio(
            sold["ClosePrice"],
            sold["ListPrice"]
        )

    # Price per square foot
    if {"ClosePrice", "LivingArea"}.issubset(sold.columns):
        sold["PricePerSquareFoot"] = safe_ratio(
            sold["ClosePrice"],
            sold["LivingArea"]
        )

    # Date features
    sold_date_columns = [
        "CloseDate",
        "PurchaseContractDate",
        "ListingContractDate"
    ]

    for column in sold_date_columns:
        if column in sold.columns:
            sold[column] = pd.to_datetime(
                sold[column],
                errors="coerce"
            )

    if "CloseDate" in sold.columns:
        sold["SaleYear"] = sold["CloseDate"].dt.year
        sold["SaleMonth"] = sold["CloseDate"].dt.month
        sold["SaleYearMonth"] = (
            sold["CloseDate"].dt.to_period("M").astype("string")
        )

    if {
        "ListingContractDate",
        "PurchaseContractDate"
    }.issubset(sold.columns):
        sold["ListingToContractDays"] = (
            sold["PurchaseContractDate"] -
            sold["ListingContractDate"]
        ).dt.days

    if {
        "PurchaseContractDate",
        "CloseDate"
    }.issubset(sold.columns):
        sold["ContractToCloseDays"] = (
            sold["CloseDate"] -
            sold["PurchaseContractDate"]
        ).dt.days

    sold = create_school_district_field(sold)

    sold_output = (
        PROCESSED_DIR / "sold_feature_engineered.csv"
    )
    sold.to_csv(sold_output, index=False)

    # Required grouped summaries
    sold_groups = {
        "PropertyType": "sold_by_property_type.csv",
        "PropertySubType": "sold_by_property_subtype.csv",
        "CountyOrParish": "sold_by_county.csv",
        "MLSAreaMajor": "sold_by_mls_area.csv",
        "ListOfficeName": "sold_by_listing_office.csv",
        "BuyerOfficeName": "sold_by_buyer_office.csv",
        "SchoolDistrict": "sold_by_school_district.csv"
    }

    for group_column, output_name in sold_groups.items():
        save_grouped_summary(
            sold,
            group_column,
            "ClosePrice",
            output_name
        )

    sample_columns = [
        column for column in [
            "ListingId",
            "ClosePrice",
            "OriginalListPrice",
            "CloseToOriginalListPriceRatio",
            "LivingArea",
            "PricePerSquareFoot",
            "DaysOnMarket",
            "ListingToContractDays",
            "ContractToCloseDays",
            "CountyOrParish",
            "SchoolDistrict",
            "SaleYearMonth"
        ]
        if column in sold.columns
    ]

    sold[sample_columns].head(100).to_csv(
        OUTPUT_DIR / "week6_sold_sample_output.csv",
        index=False
    )

    print(f"Sold rows processed: {len(sold):,}")
    print(f"Saved: {sold_output}")

    del sold
    gc.collect()

else:
    print(f"File not found: {sold_file}")


# =========================================================
# ACTIVE LISTING FEATURE ENGINEERING
# =========================================================
listings_file = PROCESSED_DIR / "listings_cleaned.csv"

if listings_file.exists():
    print("\nLoading cleaned listing data...")
    listings = pd.read_csv(
        listings_file,
        low_memory=False
    )

    listing_numeric_columns = [
        "ListPrice",
        "OriginalListPrice",
        "LivingArea",
        "DaysOnMarket"
    ]

    for column in listing_numeric_columns:
        if column in listings.columns:
            listings[column] = pd.to_numeric(
                listings[column],
                errors="coerce"
            )

    if {"ListPrice", "LivingArea"}.issubset(listings.columns):
        listings["ListPricePerSquareFoot"] = safe_ratio(
            listings["ListPrice"],
            listings["LivingArea"]
        )

    if "ListingContractDate" in listings.columns:
        listings["ListingContractDate"] = pd.to_datetime(
            listings["ListingContractDate"],
            errors="coerce"
        )

        listings["ListingYear"] = (
            listings["ListingContractDate"].dt.year
        )
        listings["ListingMonth"] = (
            listings["ListingContractDate"].dt.month
        )
        listings["ListingYearMonth"] = (
            listings["ListingContractDate"]
            .dt.to_period("M")
            .astype("string")
        )

    listings = create_school_district_field(listings)

    listings_output = (
        PROCESSED_DIR / "listings_feature_engineered.csv"
    )
    listings.to_csv(listings_output, index=False)

    listing_groups = {
        "PropertyType": "listings_by_property_type.csv",
        "PropertySubType": "listings_by_property_subtype.csv",
        "CountyOrParish": "listings_by_county.csv",
        "MLSAreaMajor": "listings_by_mls_area.csv",
        "ListOfficeName": "listings_by_listing_office.csv",
        "SchoolDistrict": "listings_by_school_district.csv"
    }

    for group_column, output_name in listing_groups.items():
        save_grouped_summary(
            listings,
            group_column,
            "ListPrice",
            output_name
        )

    print(f"Listing rows processed: {len(listings):,}")
    print(f"Saved: {listings_output}")

    del listings
    gc.collect()

else:
    print(f"File not found: {listings_file}")

print("\nWeek 6 feature engineering complete.")
