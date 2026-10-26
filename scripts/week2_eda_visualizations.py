#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 18:24:44 2026

@author: diyaapatel
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Project folders
BASE_DIR = Path("/Users/diyaapatel/Desktop/IDX-Exchange-Internship-Data")
INPUT_FILE = BASE_DIR / "processed" / "combined_sold_residential.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
GRAPH_DIR = OUTPUT_DIR / "eda_graphs"

OUTPUT_DIR.mkdir(exist_ok=True)
GRAPH_DIR.mkdir(exist_ok=True)

# Columns required for analysis
numeric_columns = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt"
]

additional_columns = [
    "CountyOrParish",
    "CloseDate",
    "ListingContractDate"
]

# Read only available columns to reduce memory usage
available_columns = pd.read_csv(INPUT_FILE, nrows=0).columns.tolist()
columns_to_load = [
    column for column in numeric_columns + additional_columns
    if column in available_columns
]

df = pd.read_csv(
    INPUT_FILE,
    usecols=columns_to_load,
    low_memory=False
)

print(f"Rows loaded: {len(df):,}")
print(f"Columns loaded: {len(df.columns)}")

# Convert numeric columns
available_numeric = [
    column for column in numeric_columns
    if column in df.columns
]

for column in available_numeric:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Percentile summary
percentile_summary = df[available_numeric].describe(
    percentiles=[0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]
).T

percentile_summary["median"] = df[available_numeric].median()
percentile_summary.to_csv(
    OUTPUT_DIR / "eda_numeric_percentiles.csv"
)

# Outlier summary and graphs
outlier_results = []

for column in available_numeric:
    values = df[column].dropna()

    if values.empty:
        continue

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1
    lower_limit = q1 - (1.5 * iqr)
    upper_limit = q3 + (1.5 * iqr)

    outlier_count = (
        (values < lower_limit) | (values > upper_limit)
    ).sum()

    outlier_results.append({
        "Variable": column,
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr,
        "LowerLimit": lower_limit,
        "UpperLimit": upper_limit,
        "OutlierCount": outlier_count,
        "OutlierPercent": (outlier_count / len(values)) * 100
    })

    # Trim only the graph to the 1st–99th percentile.
    # The original dataset is not changed.
    graph_lower = values.quantile(0.01)
    graph_upper = values.quantile(0.99)
    graph_values = values[
        values.between(graph_lower, graph_upper)
    ]

    figure, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].hist(
        graph_values,
        bins=40,
        color="steelblue",
        edgecolor="white"
    )
    axes[0].set_title(f"{column} Distribution")
    axes[0].set_xlabel(column)
    axes[0].set_ylabel("Number of Properties")

    axes[1].boxplot(graph_values, vert=False)
    axes[1].set_title(f"{column} Boxplot")
    axes[1].set_xlabel(column)

    figure.suptitle(
        f"{column}: Values Between 1st and 99th Percentiles"
    )
    plt.tight_layout()
    plt.savefig(
        GRAPH_DIR / f"{column}_distribution.png",
        dpi=200,
        bbox_inches="tight"
    )
    plt.close()

outlier_summary = pd.DataFrame(outlier_results)
outlier_summary.to_csv(
    OUTPUT_DIR / "eda_outlier_summary.csv",
    index=False
)

# Key findings
findings = []

if "ClosePrice" in df.columns:
    findings.append(
        f"Average close price: ${df['ClosePrice'].mean():,.2f}"
    )
    findings.append(
        f"Median close price: ${df['ClosePrice'].median():,.2f}"
    )

if "DaysOnMarket" in df.columns:
    findings.append(
        f"Average days on market: "
        f"{df['DaysOnMarket'].mean():,.2f}"
    )
    findings.append(
        f"Median days on market: "
        f"{df['DaysOnMarket'].median():,.2f}"
    )

if {"ClosePrice", "OriginalListPrice"}.issubset(df.columns):
    price_data = df[
        ["ClosePrice", "OriginalListPrice"]
    ].dropna()

    price_data = price_data[
        (price_data["ClosePrice"] > 0) &
        (price_data["OriginalListPrice"] > 0)
    ]

    total_sales = len(price_data)
    above = (
        price_data["ClosePrice"] >
        price_data["OriginalListPrice"]
    ).sum()
    below = (
        price_data["ClosePrice"] <
        price_data["OriginalListPrice"]
    ).sum()
    equal = (
        price_data["ClosePrice"] ==
        price_data["OriginalListPrice"]
    ).sum()

    if total_sales > 0:
        findings.append(
            f"Sold above original list price: "
            f"{above / total_sales * 100:.2f}%"
        )
        findings.append(
            f"Sold below original list price: "
            f"{below / total_sales * 100:.2f}%"
        )
        findings.append(
            f"Sold at original list price: "
            f"{equal / total_sales * 100:.2f}%"
        )

if {"CountyOrParish", "ClosePrice"}.issubset(df.columns):
    county_summary = (
        df.dropna(subset=["CountyOrParish", "ClosePrice"])
        .groupby("CountyOrParish")["ClosePrice"]
        .agg(["count", "mean", "median"])
        .sort_values("median", ascending=False)
    )

    county_summary.to_csv(
        OUTPUT_DIR / "county_price_summary.csv"
    )

if {"CloseDate", "ListingContractDate"}.issubset(df.columns):
    close_dates = pd.to_datetime(
        df["CloseDate"],
        errors="coerce"
    )
    listing_dates = pd.to_datetime(
        df["ListingContractDate"],
        errors="coerce"
    )

    inconsistent_dates = (
        close_dates < listing_dates
    ).sum()

    findings.append(
        f"Records with close date before listing date: "
        f"{inconsistent_dates:,}"
    )

# Save findings
findings_file = OUTPUT_DIR / "week2_key_findings.txt"

with open(findings_file, "w") as file:
    for finding in findings:
        file.write(finding + "\n")
        print(finding)

print("\nWeek 2 EDA visualizations complete.")
print(f"Graphs saved in: {GRAPH_DIR}")
print(f"Summaries saved in: {OUTPUT_DIR}")
