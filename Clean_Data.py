import os
import json
import gspread
import pandas as pd
import pycountry
import langcodes
import re
from langdetect import detect, LangDetectException
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask

app = Flask(__name__)

# Define the scope for the credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

google_credentials_json = os.getenv('GOOGLE_CREDENTIALS')

if google_credentials_json:
    # Load the credentials from the JSON obtained from the environment variable
    creds_dict = json.loads(google_credentials_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
else:
    print("Google credentials not found in the environment variable.")

@app.route("/")
def home():
    return("app server is running")

@app.route("/clean", methods=["POST"])
def cleaning():
    # Read the data from the spreadsheet
    data = pd.DataFrame(worksheet1.get_all_records())

    # Verify data loading
    print("Original data loaded:")
    print(data.head())  # Print the first rows for verification

    # Clean the columns except for the special ones
    for column in required_columns:
        if column not in special_columns:
            data[column] = data[column].apply(clean_text)

    # Get the last row with data in the destination sheet (worksheet2)
    existing_data = worksheet2.get_all_values()
    last_row = len(existing_data)

    # If it's the first insertion (only a header row), insert the header as well
    if last_row == 0:
        worksheet2.append_rows([data.columns.values.tolist()], value_input_option='RAW')
        last_row = 1  # The header occupies the first row

    # Add a "Row Number" column that starts at the correct row
    data["Row Number"] = range(last_row + 1, last_row + len(data) + 1)

    # Write the cleaned data to sheet 2 (appending to the end) without the header
    worksheet2.append_rows(data.values.tolist(), value_input_option='RAW')

    # Success message
    return jsonify({"message": "The data has been cleaned and successfully added to the end of sheet 2."}), 200

# Open the spreadsheet using the URL
sheet_url = os.getenv('sheetData')
sheet = client.open_by_url(sheet_url)

# Access sheet 1 (index 0) to read the original data
worksheet1 = sheet.get_worksheet(0)
data = pd.DataFrame(worksheet1.get_all_records())

# Verify data loading
print("Original data loaded:")
print(data.head())  # Print the first rows for verification

# Required columns for filtering
required_columns = [
    "Profile Url", "Full Name", "First Name", "Last Name", "Job Title", "Additional Info", 
    "Location", "Company", "Company Url", "Industry", "Company 2", "Company Url 2", 
    "Job Date Range", "Job Title 2", "Job Date Range 2", "School", "School Degree",
    "School Date Range", "School 2", "School Degree 2", "School Date Range 2"]

data = data[required_columns]

# Replacement dictionary to fix common encoding errors
replacement_dict = {
    "Ã¡": "á", "Ã©": "é", "Ã­": "í", "Ã³": "ó", "Ãº": "ú",
    "Ã±": "ñ", "Ã": "Ñ", "â": "'", "â": "-", "Ã¼": "ü",
    "â€œ": "\"", "â€": "\"", "â€˜": "'", "â€¢": "-", "â‚¬": "€",
    "â„¢": "™", "âˆ’": "-", "Â": ""
}

# Special columns where special character removal is not applied
special_columns = {"email", "mail", "linkedinProfile", "baseUrl", "professionalEmail"}

# Function to clean text in non-special columns
def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text)  # Convert to string to handle non-text values
    for bad, good in replacement_dict.items():
        text = text.replace(bad, good)
    return re.sub(r'[^\w\s-]', '', text).strip()

# Clean the columns except for the special ones
for column in required_columns:
    if column not in special_columns:
        data[column] = data[column].apply(clean_text)

# Verify the columns after cleaning
print("Data after cleaning:")
print(data.head())

# Access sheet 2 (index 1) to write the cleaned data
worksheet2 = sheet.worksheet('Sheet6')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

