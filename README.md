# SentinelLake

SentinelLake is a beginner-friendly Python tool for checking the quality of CSV data.

## Current capabilities

SentinelLake can:

- Read a UTF-8, comma-separated CSV file with a header row
- Reject an empty CSV file or a CSV file without a header row
- Show the total number of rows and column names
- Count blank values in every column
- Count exact duplicate rows
- Show a profile for every column
  - Number of non-empty values
  - Number of unique non-empty values
- Validate an `age` column when it exists
  - A non-blank age must be a whole number from 0 to 120
- Save the analysis as a JSON report file
- Show friendly errors for missing files, folders, and invalid CSV input

## Usage

From the SentinelLake project folder:

```text
python run_analysis.py data\sample_customers.csv

virtual env ".venv\Scripts\activate"