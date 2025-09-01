import requests
import datetime
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === CONFIGURATION GOOGLE SHEETS ===
SPREADSHEET_NAME = "forex"
WORKSHEET_NAME = "forex"

# === CONFIGURATION FOREX FACTORY ===
CSV_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.csv"
LOCAL_CSV = "forexfactory.csv"


def download_csv():
    """Télécharge le fichier CSV de ForexFactory"""
    response = requests.get(CSV_URL)
    if response.status_code == 200:
        with open(LOCAL_CSV, "wb") as f:
            f.write(response.content)
        print("✅ Fichier CSV ForexFactory téléchargé avec succès.")
    else:
        print(f"❌ Erreur téléchargement CSV : {response.status_code}")


def upload_to_google_sheets():
    """Charge le CSV dans Google Sheets"""
    # Authentification Google Sheets
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)

    # Lecture du CSV
    df = pd.read_csv(LOCAL_CSV)

    # Clear feuille et recharger
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("✅ Google Sheets mis à jour avec les données ForexFactory.")


if __name__ == "__main__":
    download_csv()
    upload_to_google_sheets()
