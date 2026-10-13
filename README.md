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

## Data Privacy

CSV files, raw MLS data, processed datasets, and login credentials are not included in this public repository.
