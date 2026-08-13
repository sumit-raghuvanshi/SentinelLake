# SentinelLake

SentinelLake is a beginner-friendly Python tool for checking the quality of CSV data.

## Current capabilities

SentinelLake can:

- Read a UTF-8, comma-separated CSV file
- Show the total number of rows and column names
- Count blank values in every column
- Count exact duplicate rows
- Validate an `age` column when it exists
  - A non-blank age must be a whole number from 0 to 120
- Show a friendly error when the CSV file path does not exist

## Usage

From the SentinelLake project folder:

```text
python run_analysis.py data\sample_customers.csv

//virtudal env ".venv\Scripts\activate"