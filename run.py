import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

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

# Exporatory Data Analysis (EDA) on the dataset and gain insights into the patterns and relationships between variables.
# Using libraries Matplotlib and Seaborn to create visualizations.
# Visualize the average temperature by month

# Visualize the distribution of temperature.
plt.figure(figsize=(8, 6))
sns.histplot(data=df, x='Temperature (C)', bins=30)
plt.title('Temperature Distribution')
plt.xlabel('Temperature (C)')
plt.ylabel('Count')
plt.show()

# Convert the plot to a base64-encoded image
buffer = BytesIO()
plt.savefig(buffer, format='png')
buffer.seek(0)
image_base64 = base64.b64encode(buffer.getvalue()).decode()

# Insert the image into the Google Spreadsheet
analyzed_sheet = SHEET.worksheet('analyzed')
analyzed_sheet.update([[f'=IMAGE("data:image/png;base64,{image_base64}", 1)']], 'A1')

plt.close()

# Visualize the relationship between temperature and humidity
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='Temperature (C)', y='Humidity')
plt.title('Temperature vs Humidity')
plt.xlabel('Temperature (C)')
plt.ylabel('Humidity')
plt.show()

# Convert the plot to a base64-encoded image
buffer = BytesIO()
plt.savefig(buffer, format='png')
buffer.seek(0)
image_base64 = base64.b64encode(buffer.getvalue()).decode()