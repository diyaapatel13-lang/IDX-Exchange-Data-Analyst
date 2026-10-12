"""
Week 1: Monthly MLS Dataset Aggregation

Purpose:
Combine monthly CRMLS listing and sold CSV files, filter the
datasets to residential properties, and save the combined results.

Note:
Raw and processed CSV files are stored locally and are not
uploaded to this public GitHub repository.
"""

import pandas as pd
from pathlib import Path
