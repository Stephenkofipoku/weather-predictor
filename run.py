import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
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
    sheet = client.open('weatherpredictor').worksheet('weatherhistory')
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    print(df.head())
    return df


def extract_features(df):

    """Extract relevant features for weather prediction."""
    features = df[['Datetime', 'Temperature (C)', 'Humidity',
            'Apparent Temperature (C)', 'Wind Speed (km/h)',
            'Visibility (km)', 'Pressure (millibars)']]
    return features


def handle_missing_values(df):
    """Handle missing values by removing rows with any missing values."""
    df = df.dropna()
    return df


def convert(df):
    """Perform necessary data conversions."""
    df = handle_missing_values(df)
    df = remove_irrelevant_columns(df)
    df = extract_features(df)
    df['Pressure'] = pd.to_numeric(df['Pressure (millibars)'], errors='coerce')
    df = df.drop('Pressure (millibars)', axis=1)
    print(df.head())
    return df


def remove_irrelevant_columns(df):
    """Remove irrelevant columns from the DataFrame."""
    columns_to_drop = ['Loud Cover', 'Daily Summary']
    df = df.drop(columns_to_drop, axis=1)
    return df


def visualize_temperature_distribution(df):
    """Visualize the distribution of temperature."""
    plt.figure(figsize=(8, 6))
    sns.histplot(data=df, x='Temperature (C)', bins=30)
    plt.title('Temperature Distribution')
    plt.xlabel('Temperature (C)')
    plt.ylabel('Count')
    plt.show()


def visualize_temperature_vs_humidity(df):
    """Visualize the relationship between temperature and humidity."""
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x='Temperature (C)', y='Humidity')
    plt.title('Temperature vs Humidity')
    plt.xlabel('Temperature (C)')
    plt.ylabel('Humidity')
    plt.show()


def visualize_avg_temp_by_month(df):
    """Visualize the average temperature by month."""
    df['Datetime'] = pd.to_datetime(df['Datetime'], format='%Y-%m-%d %H:%M', errors='coerce')
    df['Month'] = df['Datetime'].dt.month
    avg_temp_by_month = df.groupby('Month')['Temperature (C)'].mean().reset_index()

    plt.figure(figsize=(8, 6))
    sns.barplot(data=avg_temp_by_month, x='Month', y='Temperature (C)')
    plt.title('AverageTemperature by Month')
    plt.xlabel('Month')
    plt.ylabel('AverageTemperature (C)')
    plt.show()


def apply_linear_regression(df):
    """Apply Linear Regression to the weather prediction data."""
    X = df[['Apparent Temperature (C)', 'Humidity', 'Wind Speed (km/h)', 'Visibility (km)',
        'Pressure']]
    y = df['Temperature (C)']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Print the coefficients
    print("Mean Squared Error:", mse)
    print("R-squared:", r2)


def upload_image_to_drive(file_path, folder_id, credentials):
    """Upload an image to Google Drive."""
    drive_service = build('drive', 'v3', credentials=credentials)
    file_metadata = {
        'name': file_path,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='image/png')
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    image_id = uploaded_file['id']
    return image_id


def insert_image_into_spreadsheet(client, sheet_name, image_url, cell):
    """Insert an image into the specified cell in the Google Spreadsheet."""
    sheet = client.open('weatherpredictor').worksheet('analyzed')
    sheet.update(cell, [[f'=IMAGE("{image_url}", 1)']])


def main():
    # Authorize Google Sheets API
    gspread_client = authorize_google_sheets()

    # Read data from the 'weatherhistory' sheet into a Pandas DataFrame
    df = read_data_from_sheet(gspread_client, 'weatherhistory')
    print(df.head())

    # Handle missing values
    df = handle_missing_values(df)
    print(df.head())

    # Convert data types if necessary
    df = convert(df)
    print(df.head())

    # Call the function to visualize the temperature distribution
    visualize_temperature_distribution(df)

    # Call the function to visualize the temperature vs humidity
    visualize_temperature_vs_humidity(df)

    # Call the function to visualize the average temperature by month
    visualize_avg_temp_by_month(df)

    # Apply Linear Regression to the weather prediction data
    apply_linear_regression(df)

    # Save the visualization as an image
    plt.savefig('temperature_by_month.png')

    # Upload the image to Google Drive
    folder_id = '16MULELlzRGqHKq8ZXUDdd-JrV1nziSeI'
    creds = Credentials.from_service_account_file('creds.json')
    scoped_creds = creds.with_scopes(SCOPE)
    image_id = upload_image_to_drive('temperature_by_month.png', folder_id, scoped_creds)

    # Insert the image into the 'analyzed' sheet of the 'weatherpredictor' spreadsheet
    insert_image_into_spreadsheet(gspread_client, 'analyzed', image_id, 'A1')

    # Collect input features from the user or obtain real-time data
    apparent_temperature = float(input("Enter the apparent temperature (C): "))
    humidity = float(input("Enter the humidity: "))
    wind_speed = float(input("Enter the wind speed (km/h): "))
    visibility = float(input("Enter the visibility (km): "))
    pressure = float(input("Enter the pressure: "))


# Call the main function to execute the code
if __name__ == "__main__":
    main()