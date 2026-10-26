#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 18:48:41 2026

@author: diyaapatel
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# Project folders
# ---------------------------------------------------------
BASE_DIR = Path("/Users/diyaapatel/Desktop/IDX-Exchange-Internship-Data")
PROCESSED_DIR = BASE_DIR / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"
GRAPH_DIR = OUTPUT_DIR / "outlier_graphs"

OUTPUT_DIR.mkdir(exist_ok=True)
GRAPH_DIR.mkdir(exist_ok=True)

INPUT_FILE = PROCESSED_DIR / "sold_feature_engineered.csv"

print("Loading feature-engineered sold data...")
df = pd.read_csv(INPUT_FILE, low_memory=False)

OUTLIER_COLUMNS = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket"
]

available_columns = [
    column for column in OUTLIER_COLUMNS
    if column in df.columns
]

for column in available_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

starting_rows = len(df)
starting_medians = df[available_columns].median()

print(f"Starting rows: {starting_rows:,}")

outlier_summary = []

# ---------------------------------------------------------
# Create IQR outlier flags
# ---------------------------------------------------------
for column in available_columns:
    values = df[column].dropna()

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1

    lower_limit = q1 - (1.5 * iqr)
    upper_limit = q3 + (1.5 * iqr)

    flag_column = f"{column}_iqr_outlier_flag"

    df[flag_column] = (
        df[column].notna() &
        (
            (df[column] < lower_limit) |
            (df[column] > upper_limit)
        )
    )

    outlier_count = int(df[flag_column].sum())

    outlier_summary.append({
        "Variable": column,
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr,
        "LowerLimit": lower_limit,
        "UpperLimit": upper_limit,
        "OutlierCount": outlier_count,
        "OutlierPercent": (
            outlier_count / starting_rows * 100
        )
    })

    print(
        f"{column}: {outlier_count:,} outliers "
        f"({outlier_count / starting_rows * 100:.2f}%)"
    )

# Flag a row when any required field is an outlier.
flag_columns = [
    f"{column}_iqr_outlier_flag"
    for column in available_columns
]

df["any_iqr_outlier_flag"] = (
    df[flag_columns].any(axis=1)
)

# ---------------------------------------------------------
# Preserve both datasets
# ---------------------------------------------------------
full_flagged_file = (
    PROCESSED_DIR / "sold_full_with_outlier_flags.csv"
)

clean_file = (
    PROCESSED_DIR / "sold_outliers_filtered.csv"
)

# Full dataset is preserved with flags.
df.to_csv(full_flagged_file, index=False)

# Separate filtered dataset for analysis.
clean_df = df.loc[
    ~df["any_iqr_outlier_flag"]
].copy()

clean_df.to_csv(clean_file, index=False)

final_rows = len(clean_df)
removed_rows = starting_rows - final_rows
final_medians = clean_df[available_columns].median()

# ---------------------------------------------------------
# Save outlier and before/after summaries
# ---------------------------------------------------------
pd.DataFrame(outlier_summary).to_csv(
    OUTPUT_DIR / "week7_outlier_summary.csv",
    index=False
)

comparison_rows = [
    {
        "Metric": "Row Count",
        "BeforeFiltering": starting_rows,
        "AfterFiltering": final_rows,
        "Difference": removed_rows
    }
]

for column in available_columns:
    comparison_rows.append({
        "Metric": f"Median {column}",
        "BeforeFiltering": starting_medians[column],
        "AfterFiltering": final_medians[column],
        "Difference": (
            final_medians[column] -
            starting_medians[column]
        )
    })

comparison = pd.DataFrame(comparison_rows)

comparison.to_csv(
    OUTPUT_DIR / "week7_before_after_comparison.csv",
    index=False
)

# ---------------------------------------------------------
# Create before-and-after graphs
# ---------------------------------------------------------
for column in available_columns:
    before_values = df[column].dropna()
    after_values = clean_df[column].dropna()

    # Limit graph display to readable ranges.
    graph_upper = before_values.quantile(0.99)

    before_graph = before_values[
        before_values <= graph_upper
    ]

    after_graph = after_values[
        after_values <= graph_upper
    ]

    figure, axes = plt.subplots(
        1,
        2,
        figsize=(12, 4)
    )

    axes[0].hist(
        before_graph,
        bins=40,
        color="tomato",
        edgecolor="white"
    )
    axes[0].set_title(f"{column}: Before Filtering")
    axes[0].set_xlabel(column)
    axes[0].set_ylabel("Number of Properties")

    axes[1].hist(
        after_graph,
        bins=40,
        color="seagreen",
        edgecolor="white"
    )
    axes[1].set_title(f"{column}: After Filtering")
    axes[1].set_xlabel(column)
    axes[1].set_ylabel("Number of Properties")

    figure.suptitle(
        f"{column} Before and After IQR Filtering"
    )

    plt.tight_layout()

    plt.savefig(
        GRAPH_DIR / f"{column}_before_after.png",
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

print("\nBefore-and-after comparison:")
print(comparison.to_string(index=False))

print(f"\nRows removed from filtered copy: {removed_rows:,}")
print(f"Full flagged dataset saved: {full_flagged_file}")
print(f"Filtered dataset saved: {clean_file}")
print("\nWeek 7 outlier analysis complete.")
