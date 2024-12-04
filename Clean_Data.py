import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import pycountry
import langcodes

# Fixer la graine pour des résultats cohérents dans langdetect
DetectorFactory.seed = 0

# Authentification avec Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('js/cleandatalinkedin-db3b9e69269b.json', scope)
client = gspread.authorize(creds)

# Ouvrir la feuille de calcul partagée en utilisant l'URL
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1klDIZ9ZBhmiUZ_FwS0DejKOl8iRph6ewW4C6JAUJ598/edit?usp=sharing")

# Accéder à la Feuille 1 (index 0) pour lire les données originales
worksheet1 = sheet.get_worksheet(0)
data = pd.DataFrame(worksheet1.get_all_records())

# Vérifier le chargement des données
print("Données originales chargées :")
print(data.head())  # Imprimer les premières lignes pour vérification

# Colonnes requises à filtrer
required_columns = [
    "firstName", "lastName", "fullName", "email", "mail", "phoneNumber", "linkedinProfile", "description", 
    "headline", "location", "company", "jobTitle", "jobDescription", "jobLocation", "company2", 
    "jobTitle2", "jobDescription2", "baseUrl", "professionalEmail"
]
data = data[required_columns]

# Dictionnaire de remplacement pour corriger les erreurs courantes d'encodage
replacement_dict = {
    "Ã¡": "á", "Ã©": "é", "Ã­": "í", "Ã³": "ó", "Ãº": "ú",
    "Ã±": "ñ", "Ã": "Ñ", "â": "'", "â": "-", "Ã¼": "ü",
    "â€œ": "\"", "â€": "\"", "â€˜": "'", "â€¢": "-", "â‚¬": "€",
    "â„¢": "™", "âˆ’": "-", "Â": ""
}

# Colonnes spéciales où aucune suppression de caractères spéciaux n'est appliquée
special_columns = {"email", "mail", "linkedinProfile", "baseUrl", "professionalEmail"}

# Fonction pour nettoyer le texte dans les colonnes non spéciales
def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text)  # Convertir en chaîne pour traiter les valeurs non textuelles
    for bad, good in replacement_dict.items():
        text = text.replace(bad, good)
    return re.sub(r'[^\w\s-]', '', text).strip()

# Appliquer le nettoyage seulement aux colonnes qui ne sont pas dans `special_columns`
for column in required_columns:
    if column not in special_columns:
        data[column] = data[column].apply(clean_text)

# Vérifier les données après le nettoyage
print("Données après le nettoyage :")
print(data.head())

# Fonction pour obtenir la langue par défaut d'un pays en utilisant pycountry et langcodes
def get_language_from_country(country_name):
    try:
        country = pycountry.countries.lookup(country_name)
        language = langcodes.standardize_tag(langcodes.Language.get(country.alpha_2).language)
        return language
    except LookupError:
        return None

# Fonction pour détecter la langue en fonction du texte ou du pays
def detect_language(description, headline, location):
    for text in [description, headline]:
        if text:
            try:
                return detect(text)
            except LangDetectException:
                continue
    for country in pycountry.countries:
        if country.name.lower() in location.lower():
            lang = get_language_from_country(country.name)
            if lang:
                return lang
    return "en"

# Appliquer la détection de la langue
data['language'] = data.apply(
    lambda row: detect_language(row['description'], row['headline'], row['location']),
    axis=1
)

# Vérifier les données après la détection de la langue
print("Données après la détection de la langue :")
print(data.head())

# Accéder à la Feuille 2 (index 1) pour écrire les données nettoyées
worksheet2 = sheet.get_worksheet(1)
worksheet2.clear()

# Écrire les données dans la Feuille 2
worksheet2.update([data.columns.values.tolist()] + data.values.tolist())

print("Les données avec détection de langue ont été copiées et nettoyées avec succès dans la Feuille 2.")
