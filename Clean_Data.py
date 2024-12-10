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

# Definir el alcance de las credenciales
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

google_credentials_json = os.getenv('GOOGLE_CREDENTIALS')

if google_credentials_json:
    # Cargar las credenciales desde el JSON que se obtiene de la variable de entorno
    creds_dict = json.loads(google_credentials_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
else:
    print("No se encontraron las credenciales de Google en la variable de entorno.")

@app.route("/")
def home():
    return("app server is running")

@app.route("/clean", methods=["POST"])
def cleaning():
    # Leer los datos de la hoja de cálculo
    data = pd.DataFrame(worksheet1.get_all_records())

    # Verificar el cargado de los datos
    print("Données originales chargées :")
    print(data.head())  # Imprimir las primeras filas para verificación

    # Limpiar las columnas excepto las especiales
    for column in required_columns:
        if column not in special_columns:
            data[column] = data[column].apply(clean_text)

    # Obtener la última fila de la hoja destino antes de escribir
    last_row = len(worksheet2.get_all_values())

    # Añadir una columna de "Row Number" para saber la línea de cada fila en la hoja
    data["Row Number"] = range(last_row + 1, last_row + len(data) + 1)

    # Escribir los datos limpios en la hoja 2 (añadiendo al final)
    worksheet2.append_rows([data.columns.values.tolist()] + data.values.tolist(), value_input_option='RAW')

    # Mensaje de éxito
    return jsonify({"message": "Los datos han sido limpiados y añadidos al final de la hoja 2 con éxito."}), 200

# Abre la hoja de cálculo usando la URL
sheet_url = os.getenv('sheetData')
sheet = client.open_by_url(sheet_url)

# Acceder a la hoja 1 (index 0) para leer los datos originales
worksheet1 = sheet.get_worksheet(0)
data = pd.DataFrame(worksheet1.get_all_records())

# Verificar el cargado de los datos
print("Données originales chargées :")
print(data.head())  # Imprimir las primeras filas para verificación

# Columnas requeridas para filtrar
required_columns = [
    "Profile Url", "Full Name", "First Name", "Last Name", "Job Title", "Additional Info", 
    "Location", "Company", "Company Url", "Industry", "Company 2", "Company Url 2", 
    "Job Date Range", "Job Title 2", "Job Date Range 2", "School", "School Degree",
    "School Date Range", "School 2", "School Degree 2", "School Date Range 2"]

data = data[required_columns]

# Diccionario de reemplazo para corregir errores comunes de codificación
replacement_dict = {
    "Ã¡": "á", "Ã©": "é", "Ã­": "í", "Ã³": "ó", "Ãº": "ú",
    "Ã±": "ñ", "Ã": "Ñ", "â": "'", "â": "-", "Ã¼": "ü",
    "â€œ": "\"", "â€": "\"", "â€˜": "'", "â€¢": "-", "â‚¬": "€",
    "â„¢": "™", "âˆ’": "-", "Â": ""
}

# Columnas especiales donde no se aplica eliminación de caracteres especiales
special_columns = {"email", "mail", "linkedinProfile", "baseUrl", "professionalEmail"}

# Función para limpiar el texto en las columnas no especiales
def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text)  # Convertir en cadena para manejar valores no textuales
    for bad, good in replacement_dict.items():
        text = text.replace(bad, good)
    return re.sub(r'[^\w\s-]', '', text).strip()

# Limpiar las columnas excepto las especiales
for column in required_columns:
    if column not in special_columns:
        data[column] = data[column].apply(clean_text)

# Verificar las columnas después de limpiar
print("Données après le nettoyage :")
print(data.head())

# Acceder a la hoja 2 (index 1) para escribir los datos limpiados
worksheet2 =  sheet.worksheet('Sheet6')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

