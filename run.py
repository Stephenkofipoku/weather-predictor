import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Set up credentials and authorize the Google Sheets API

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('weatherpredictor')

# Select the desired sheet within the spreadsheet
weatherhistory = SHEET.worksheet('weatherhistory')

# Read the data from the sheet into a Pandas DataFrame
data = weatherhistory.get_all_records()
df = pd.DataFrame(data)

df = df.dropna()
"""
Handle missing values.
Remove rows with any missing values
"""

# Convert data types if necessary
df['Temperature (C)'] = pd.to_numeric(df['Temperature (C)'])
df['Precip Type'] = df['Precip Type'].astype('category')

# Remove irrelevant columns
columns_to_drop = ['Loud Cover', 'Daily Summary']
df = df.drop(columns_to_drop, axis=1)

# Display the cleaned dataset
print(df.head())
