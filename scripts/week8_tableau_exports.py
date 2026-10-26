#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 19:23:19 2026

@author: diyaapatel
"""

from pathlib import Path
import pandas as pd

# ---------------------------------------------------------
# Project folders
# ---------------------------------------------------------
BASE_DIR = Path("/Users/diyaapatel/Desktop/IDX-Exchange-Internship-Data")
PROCESSED_DIR = BASE_DIR / "processed"
TABLEAU_DIR = BASE_DIR / "tableau_exports"

TABLEAU_DIR.mkdir(exist_ok=True)

SOLD_FILE = PROCESSED_DIR / "sold_outliers_filtered.csv"
LISTINGS_FILE = PROCESSED_DIR / "listings_feature_engineered.csv"


def load_selected_columns(file_path, desired_columns):
    """Load only the columns available in the source file."""
    available = pd.read_csv(
        file_path,
        nrows=0
    ).columns.tolist()

    selected = [
        column for column in desired_columns
        if column in available
    ]

    return pd.read_csv(
        file_path,
        usecols=selected,
        low_memory=False
    )


def create_summary(df, group_column):
    """Create a Tableau-ready grouped market summary."""

    if group_column not in df.columns:
        return None

    aggregations = {}

    if "ListingId" in df.columns:
        aggregations["PropertyCount"] = (
            "ListingId",
            "nunique"
        )
    elif "ClosePrice" in df.columns:
        aggregations["PropertyCount"] = (
            "ClosePrice",
            "count"
        )

    if "ClosePrice" in df.columns:
        aggregations["AverageClosePrice"] = (
            "ClosePrice",
            "mean"
        )
        aggregations["MedianClosePrice"] = (
            "ClosePrice",
            "median"
        )

    if "ListPrice" in df.columns:
        aggregations["AverageListPrice"] = (
            "ListPrice",
            "mean"
        )
        aggregations["MedianListPrice"] = (
            "ListPrice",
            "median"
        )

    if "PricePerSquareFoot" in df.columns:
        aggregations["MedianPricePerSquareFoot"] = (
            "PricePerSquareFoot",
            "median"
        )

    if "DaysOnMarket" in df.columns:
        aggregations["MedianDaysOnMarket"] = (
            "DaysOnMarket",
            "median"
        )

    if "CloseToOriginalListPriceRatio" in df.columns:
        aggregations["AverageSaleToListRatio"] = (
            "CloseToOriginalListPriceRatio",
            "mean"
        )

    if "MortgageRate" in df.columns:
        aggregations["AverageMortgageRate"] = (
            "MortgageRate",
            "mean"
        )

    summary = (
        df.dropna(subset=[group_column])
        .groupby(group_column)
        .agg(**aggregations)
        .reset_index()
    )

    return summary


# =========================================================
# SOLD-PROPERTY TABLEAU EXPORTS
# =========================================================
sold_columns = [
    "ListingId",
    "SaleYearMonth",
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "PricePerSquareFoot",
    "DaysOnMarket",
    "CloseToOriginalListPriceRatio",
    "MortgageRate",
    "CountyOrParish",
    "PropertyType",
    "PropertySubType",
    "MLSAreaMajor",
    "SchoolDistrict",
    "ListOfficeName",
    "BuyerOfficeName"
]

print("Loading sold-property data...")
sold = load_selected_columns(
    SOLD_FILE,
    sold_columns
)

numeric_columns = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "PricePerSquareFoot",
    "DaysOnMarket",
    "CloseToOriginalListPriceRatio",
    "MortgageRate"
]

for column in numeric_columns:
    if column in sold.columns:
        sold[column] = pd.to_numeric(
            sold[column],
            errors="coerce"
        )

sold_summaries = {
    "SaleYearMonth": "tableau_monthly_sales.csv",
    "CountyOrParish": "tableau_county_sales.csv",
    "PropertyType": "tableau_property_type.csv",
    "PropertySubType": "tableau_property_subtype.csv",
    "MLSAreaMajor": "tableau_mls_area.csv",
    "SchoolDistrict": "tableau_school_district.csv",
    "ListOfficeName": "tableau_listing_office.csv",
    "BuyerOfficeName": "tableau_buyer_office.csv"
}

for group_column, file_name in sold_summaries.items():
    summary = create_summary(
        sold,
        group_column
    )

    if summary is not None:
        # Avoid publishing extremely small groups.
        if "PropertyCount" in summary.columns:
            summary = summary[
                summary["PropertyCount"] >= 10
            ]

        if group_column == "SaleYearMonth":
            summary = summary.sort_values(
                group_column
            )
        elif "PropertyCount" in summary.columns:
            summary = summary.sort_values(
                "PropertyCount",
                ascending=False
            )

        summary.to_csv(
            TABLEAU_DIR / file_name,
            index=False
        )

        print(f"Saved: {file_name}")

# Overall KPI table
kpi_data = {
    "TotalProperties": [
        sold["ListingId"].nunique()
        if "ListingId" in sold.columns
        else len(sold)
    ]
}

if "ClosePrice" in sold.columns:
    kpi_data["AverageClosePrice"] = [
        sold["ClosePrice"].mean()
    ]
    kpi_data["MedianClosePrice"] = [
        sold["ClosePrice"].median()
    ]

if "PricePerSquareFoot" in sold.columns:
    kpi_data["MedianPricePerSquareFoot"] = [
        sold["PricePerSquareFoot"].median()
    ]

if "DaysOnMarket" in sold.columns:
    kpi_data["MedianDaysOnMarket"] = [
        sold["DaysOnMarket"].median()
    ]

if "CloseToOriginalListPriceRatio" in sold.columns:
    kpi_data["AverageSaleToListRatio"] = [
        sold["CloseToOriginalListPriceRatio"].mean()
    ]

if "MortgageRate" in sold.columns:
    kpi_data["AverageMortgageRate"] = [
        sold["MortgageRate"].mean()
    ]

pd.DataFrame(kpi_data).to_csv(
    TABLEAU_DIR / "tableau_overall_kpis.csv",
    index=False
)

print("Saved: tableau_overall_kpis.csv")


# =========================================================
# ACTIVE-LISTING TABLEAU EXPORTS
# =========================================================
listing_columns = [
    "ListingId",
    "ListingYearMonth",
    "ListPrice",
    "ListPricePerSquareFoot",
    "DaysOnMarket",
    "MortgageRate",
    "CountyOrParish",
    "PropertyType",
    "PropertySubType",
    "MLSAreaMajor",
    "SchoolDistrict"
]

print("\nLoading listing data...")
listings = load_selected_columns(
    LISTINGS_FILE,
    listing_columns
)

listing_numeric = [
    "ListPrice",
    "ListPricePerSquareFoot",
    "DaysOnMarket",
    "MortgageRate"
]

for column in listing_numeric:
    if column in listings.columns:
        listings[column] = pd.to_numeric(
            listings[column],
            errors="coerce"
        )


def create_listing_summary(df, group_column):
    if group_column not in df.columns:
        return None

    aggregations = {}

    if "ListingId" in df.columns:
        aggregations["ListingCount"] = (
            "ListingId",
            "nunique"
        )
    else:
        aggregations["ListingCount"] = (
            "ListPrice",
            "count"
        )

    if "ListPrice" in df.columns:
        aggregations["AverageListPrice"] = (
            "ListPrice",
            "mean"
        )
        aggregations["MedianListPrice"] = (
            "ListPrice",
            "median"
        )

    if "ListPricePerSquareFoot" in df.columns:
        aggregations["MedianListPricePerSquareFoot"] = (
            "ListPricePerSquareFoot",
            "median"
        )

    if "DaysOnMarket" in df.columns:
        aggregations["MedianDaysOnMarket"] = (
            "DaysOnMarket",
            "median"
        )

    if "MortgageRate" in df.columns:
        aggregations["AverageMortgageRate"] = (
            "MortgageRate",
            "mean"
        )

    return (
        df.dropna(subset=[group_column])
        .groupby(group_column)
        .agg(**aggregations)
        .reset_index()
    )


listing_summaries = {
    "ListingYearMonth": "tableau_monthly_listings.csv",
    "CountyOrParish": "tableau_county_listings.csv",
    "PropertySubType": "tableau_listing_subtypes.csv"
}

for group_column, file_name in listing_summaries.items():
    summary = create_listing_summary(
        listings,
        group_column
    )

    if summary is not None:
        if "ListingCount" in summary.columns:
            summary = summary[
                summary["ListingCount"] >= 10
            ]

        summary.to_csv(
            TABLEAU_DIR / file_name,
            index=False
        )

        print(f"Saved: {file_name}")

print(f"\nTableau files saved in: {TABLEAU_DIR}")
print("Week 8 Tableau exports complete.")
