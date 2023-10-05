import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Set up credentials and authorize the Google Sheets API

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

def authorize_google_sheets():
    """Authorize and return the Google Sheets client."""
    creds = Credentials.from_service_account_file('creds.json')
    scoped_creds = creds.with_scopes(SCOPE)
    gspread_client = gspread.authorize(scoped_creds)
    return gspread_client

def read_data_from_sheet(client, sheet_name):
    """Read data from the specified sheet in the Google Spreadsheet."""
    sheet = client.open('weatherpredictor').worksheet(sheet_name)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df
    
def handle_missing_values(df):
    """Handle missing values by removing rows with any missing values."""
    df = df.dropna()
    return df

# Convert data types if necessary
df['Temperature (C)'] = pd.to_numeric(df['Temperature (C)'])
df['Precip Type'] = df['Precip Type'].astype('category')

# Remove irrelevant columns
columns_to_drop = ['Loud Cover', 'Daily Summary']
df = df.drop(columns_to_drop, axis=1)

# Exporatory Data Analysis (EDA) on the dataset and gain insights into the dataset and relationships between variables.
# Using libraries Matplotlib and Seaborn to create visualizations.
# Visualize the average temperature by month

# Visualize the distribution of temperature.
plt.figure(figsize=(8, 6))
sns.histplot(data=df, x='Temperature (C)', bins=30)
plt.title('Temperature Distribution')
plt.xlabel('Temperature (C)')
plt.ylabel('Count')
plt.savefig('temperature_distribution.png')
plt.close()

# Upload the temperature distribution image to Google Drive
drive_service = build('drive', 'v3', credentials=SCOPED_CREDS)
file_metadata = {
    'name': 'temperature_distribution.png',
    'parents': [SHEET.id]
}
media = MediaFileUpload('temperature_distribution.png', mimetype='image/png')
uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
image_url = f"https://drive.google.com/uc?id={uploaded_file['id']}"

# Insert the temperature distribution image into the Google Spreadsheet
analyzed_sheet = SHEET.worksheet('analyzed')
analyzed_sheet.update('A1', [[f'=IMAGE("{image_url}", 1)']])

# Visualize the relationship between temperature and humidity
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='Temperature (C)', y='Humidity')
plt.title('Temperature vs Humidity')
plt.xlabel('Temperature (C)')
plt.ylabel('Humidity')
plt.savefig('temperature_vs_humidity.png')
plt.close()

# Upload the temperature vs. humidity image to Google Drive
file_metadata = {
    'name': 'temperature_vs_humidity.png',
    'parents': [SHEET.id]
}
media = MediaFileUpload('temperature_vs_humidity.png', mimetype='image/png')
uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
image_url = f"https://drive.google.com/uc?id={uploaded_file['id']}"

# Insert the temperature vs. humidity image into the Google Spreadsheet
analyzed_sheet.update('D1', [[f'=IMAGE("{image_url}", 1)']])

# Print the plots in the terminal
sns.histplot(data=df, x='Temperature (C)', bins=30)
plt.title('Temperature Distribution')
plt.xlabel('Temperature (C)')
plt.ylabel('Count')
plt.show()

sns.scatterplot(data=df, x='Temperature (C)', y='Humidity')
plt.title('Temperature vs Humidity')
plt.xlabel('Temperature (C)')
plt.ylabel('Humidity')
plt.show()