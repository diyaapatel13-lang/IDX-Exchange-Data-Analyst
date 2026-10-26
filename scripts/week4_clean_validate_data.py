from pathlib import Path
import gc
import pandas as pd

# ---------------------------------------------------------
# Project folders
# ---------------------------------------------------------
BASE_DIR = Path("/Users/diyaapatel/Desktop/IDX-Exchange-Internship-Data")
PROCESSED_DIR = BASE_DIR / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

DATASETS = {
    "listings": PROCESSED_DIR / "listings_with_mortgage_rates.csv",
    "sold": PROCESSED_DIR / "sold_with_mortgage_rates.csv"
}

DATE_COLUMNS = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate",
    "OnMarketDate",
    "OffMarketDate",
    "PendingTimestamp",
    "StatusChangeTimestamp"
]

NUMERIC_COLUMNS = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
    "Latitude",
    "Longitude",
    "MortgageRate"
]


def clean_and_validate(dataset_name, input_file):
    print(f"\nProcessing {dataset_name}: {input_file.name}")

    df = pd.read_csv(input_file, low_memory=False)

    starting_rows = len(df)
    starting_columns = len(df.columns)

    print(f"Starting rows: {starting_rows:,}")
    print(f"Starting columns: {starting_columns}")

    # Remove unnamed export columns and duplicated column names.
    unnamed_columns = [
        column for column in df.columns
        if column.startswith("Unnamed:")
    ]

    if unnamed_columns:
        df = df.drop(columns=unnamed_columns)

    df = df.loc[:, ~df.columns.duplicated()]

    # Convert required date fields.
    available_date_columns = [
        column for column in DATE_COLUMNS
        if column in df.columns
    ]

    for column in available_date_columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    # Convert required numeric fields.
    available_numeric_columns = [
        column for column in NUMERIC_COLUMNS
        if column in df.columns
    ]

    for column in available_numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # -----------------------------------------------------
    # Invalid numeric-value flags
    # -----------------------------------------------------
    numeric_rules = {
        "ClosePrice": lambda values: values <= 0,
        "ListPrice": lambda values: values <= 0,
        "OriginalListPrice": lambda values: values <= 0,
        "LivingArea": lambda values: values <= 0,
        "LotSizeAcres": lambda values: values < 0,
        "BedroomsTotal": lambda values: values < 0,
        "BathroomsTotalInteger": lambda values: values < 0,
        "DaysOnMarket": lambda values: values < 0,
        "YearBuilt": lambda values: (
            (values < 1700) |
            (values > pd.Timestamp.now().year)
        )
    }

    for column, rule in numeric_rules.items():
        if column in df.columns:
            flag_name = f"invalid_{column.lower()}_flag"
            df[flag_name] = (
                df[column].notna() &
                rule(df[column])
            )

    # -----------------------------------------------------
    # Required timeline validation flags
    # -----------------------------------------------------
    if {"ListingContractDate", "CloseDate"}.issubset(df.columns):
        df["listing_after_close_flag"] = (
            df["ListingContractDate"].notna() &
            df["CloseDate"].notna() &
            (df["ListingContractDate"] > df["CloseDate"])
        )
    else:
        df["listing_after_close_flag"] = False

    if {"PurchaseContractDate", "CloseDate"}.issubset(df.columns):
        df["purchase_after_close_flag"] = (
            df["PurchaseContractDate"].notna() &
            df["CloseDate"].notna() &
            (df["PurchaseContractDate"] > df["CloseDate"])
        )
    else:
        df["purchase_after_close_flag"] = False

    df["negative_timeline_flag"] = (
        df["listing_after_close_flag"] |
        df["purchase_after_close_flag"]
    )

    if {
        "ListingContractDate",
        "PurchaseContractDate"
    }.issubset(df.columns):
        df["purchase_before_listing_flag"] = (
            df["PurchaseContractDate"].notna() &
            df["ListingContractDate"].notna() &
            (
                df["PurchaseContractDate"] <
                df["ListingContractDate"]
            )
        )
        df["negative_timeline_flag"] = (
            df["negative_timeline_flag"] |
            df["purchase_before_listing_flag"]
        )

    # -----------------------------------------------------
    # Geographic validation flags
    # -----------------------------------------------------
    if {"Latitude", "Longitude"}.issubset(df.columns):
        df["missing_coordinates_flag"] = (
            df["Latitude"].isna() |
            df["Longitude"].isna()
        )

        df["zero_coordinates_flag"] = (
            (df["Latitude"] == 0) |
            (df["Longitude"] == 0)
        )

        df["positive_longitude_flag"] = (
            df["Longitude"].notna() &
            (df["Longitude"] > 0)
        )

        df["outside_california_flag"] = (
            df["Latitude"].notna() &
            df["Longitude"].notna() &
            (
                (df["Latitude"] < 32.5) |
                (df["Latitude"] > 42.1) |
                (df["Longitude"] < -124.5) |
                (df["Longitude"] > -114.0)
            )
        )
    else:
        df["missing_coordinates_flag"] = True
        df["zero_coordinates_flag"] = False
        df["positive_longitude_flag"] = False
        df["outside_california_flag"] = False

    geographic_columns = [
        column for column in [
            "City",
            "CountyOrParish",
            "StateOrProvince",
            "PostalCode"
        ]
        if column in df.columns
    ]

    if geographic_columns:
        df["missing_geography_flag"] = (
            df[geographic_columns].isna().any(axis=1)
        )
    else:
        df["missing_geography_flag"] = True

    # -----------------------------------------------------
    # Duplicate identifier check
    # -----------------------------------------------------
    identifier_options = [
        "ListingId",
        "ListingKey",
        "ListingKeyNumeric"
    ]

    identifier_column = next(
        (
            column for column in identifier_options
            if column in df.columns
        ),
        None
    )

    if identifier_column:
        df["duplicate_listing_identifier_flag"] = (
            df[identifier_column].notna() &
            df[identifier_column].duplicated(keep=False)
        )
    else:
        df["duplicate_listing_identifier_flag"] = False

    # -----------------------------------------------------
    # Save documentation and summaries
    # -----------------------------------------------------
    missing_summary = (
        df.isna()
        .sum()
        .sort_values(ascending=False)
        .rename("MissingValues")
        .to_frame()
    )

    missing_summary["MissingPercent"] = (
        missing_summary["MissingValues"] / len(df) * 100
    )

    missing_summary.to_csv(
        OUTPUT_DIR / f"{dataset_name}_missing_values.csv"
    )

    datatype_summary = pd.DataFrame({
        "Column": df.columns,
        "DataType": df.dtypes.astype(str).values
    })

    datatype_summary.to_csv(
        OUTPUT_DIR / f"{dataset_name}_datatype_confirmation.csv",
        index=False
    )

    flag_columns = [
        column for column in df.columns
        if column.endswith("_flag")
    ]

    validation_summary = pd.DataFrame({
        "Flag": flag_columns,
        "FlaggedRows": [
            int(df[column].sum())
            for column in flag_columns
        ]
    })

    validation_summary.to_csv(
        OUTPUT_DIR / f"{dataset_name}_validation_summary.csv",
        index=False
    )

    output_file = (
        PROCESSED_DIR / f"{dataset_name}_cleaned.csv"
    )

    df.to_csv(output_file, index=False)

    final_rows = len(df)
    final_columns = len(df.columns)

    print(f"Final rows: {final_rows:,}")
    print(f"Final columns: {final_columns}")
    print(f"Rows removed: {starting_rows - final_rows:,}")
    print(
        f"Redundant export columns removed: "
        f"{starting_columns - len(df.columns) + len(flag_columns)}"
    )
    print("\nValidation summary:")
    print(validation_summary.to_string(index=False))
    print(f"\nSaved cleaned data: {output_file}")
    print(
        f"Saved validation summary: "
        f"{OUTPUT_DIR / f'{dataset_name}_validation_summary.csv'}"
    )

    del df
    gc.collect()


for name, file_path in DATASETS.items():
    if file_path.exists():
        clean_and_validate(name, file_path)
    else:
        print(f"\nFile not found: {file_path}")

print("\nWeek 4–5 cleaning and validation complete.")
