import gspread
from google.oauth2.service_account import Credentials
import Pandas as pd

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

# Display the first few rows of the dataset
print(df.head())