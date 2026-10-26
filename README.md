# IDX-Exchange-Data-Analyst

This repository contains Python scripts developed during the IDX Exchange Data Analyst Internship.

## Project Objectives

- Combine monthly CRMLS listing and sold datasets.
- Validate and explore residential real estate data.
- Enrich MLS data with monthly mortgage rates.
- Clean and prepare the datasets for analysis.
- Develop Tableau visualizations and dashboards.

## Repository Structure

- `scripts/` – Python scripts for data aggregation, validation, enrichment, and cleaning.
- `data/` – Local data files excluded from GitHub.
- `outputs/` – Local analytical outputs excluded from GitHub.

## Progress Through Week 4

### Week 1: Data Preparation
- Downloaded 28 CRMLS listing files and 27 sold files.
- Combined the monthly files into separate listing and sold datasets.
- Filtered both datasets to residential properties only.
- The FTP server contained listing data through April 2026 and sold data through March 2026.

### Week 2: Exploratory Data Analysis
- Examined dataset dimensions, data types, missing values, and property types.
- Identified columns with more than 90% missing data.
- Generated descriptive statistics for closing price, living area, and days on market.

### Week 3: Mortgage-Rate Integration
- Downloaded the FRED MORTGAGE30US mortgage-rate series.
- Calculated monthly average mortgage rates.
- Added rates to 547,162 listing records and 397,473 sold records.
- Confirmed that no valid dates were missing a mortgage-rate match.

### Week 4: Data Cleaning and Validation
- Standardized date and numeric fields.
- Flagged invalid prices, living areas, days on market, and coordinates.
- Created timeline, geographic, and duplicate-identifier validation flags.
- Saved cleaned datasets and validation summaries locally.

## Additional Progress Through Week 7

### Week 2: Exploratory Data Analysis and Visualizations

- Generated percentile summaries for nine major numeric variables.
- Created nine combined histogram and boxplot visualizations.
- Evaluated ClosePrice, ListPrice, OriginalListPrice, LivingArea, LotSizeAcres, BedroomsTotal, BathroomsTotalInteger, DaysOnMarket, and YearBuilt.
- Calculated IQR outlier counts and percentages.
- Analyzed average and median sale prices, days on market, sale-to-list-price performance, county-level prices, and inconsistent transaction dates.

### Weeks 4–5: Cleaning and Validation

- Converted required date and numeric fields to consistent data types.
- Reviewed missing values and removed redundant export columns.
- Created validation flags for invalid prices, living area, lot size, bedrooms, bathrooms, days on market, and year built.
- Validated listing, purchase-contract, and closing-date timelines.
- Checked for missing, zero, positive, and geographically implausible coordinates.
- Identified missing geographic fields and duplicate listing identifiers.
- Preserved the original row counts while documenting questionable records with validation flags.

### Week 6: Feature Engineering

- Calculated close-to-list and close-to-original-list-price ratios.
- Calculated price and list price per square foot.
- Created year, month, and year-month transaction fields.
- Calculated listing-to-contract and contract-to-close timelines.
- Combined available school-district fields.
- Created grouped summaries by property type, property subtype, county, MLS area, listing office, buyer office, and school district.

### Week 7: Outlier Analysis

- Applied the interquartile range method to ClosePrice, LivingArea, and DaysOnMarket.
- Created individual and combined outlier flags.
- Preserved a complete dataset containing all records and outlier flags.
- Created a separate filtered dataset for analytical comparisons.
- Compared row counts and median values before and after filtering.
- Generated three before-and-after distribution visualizations.

## Data Privacy

CSV files, raw MLS data, processed datasets, and login credentials are not included in this public repository.
