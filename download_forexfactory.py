# download_forexfactory.py

import os
import json
import gspread
import requests
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

SPREADSHEET_NAME = "forex"
WORKSHEET_NAME = "forex"

def get_gspread_client():
    """Initialise la connexion Google Sheets via GOOGLE_CREDS."""
    creds_env = os.getenv("GOOGLE_CREDS")
    if not creds_env:
        raise FileNotFoundError("❌ Variable GOOGLE_CREDS introuvable dans Render.")

    creds_dict = json.loads(creds_env)
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    print("✅ Connexion Google Sheets réussie")
    return client

def download_forexfactory_csv():
    """Télécharge le CSV ForexFactory en testant plusieurs URLs alternatives."""
    urls = [
        "https://cdn-nfs.forexfactory.net/ff_calendar_thisweek.csv",  # tentative 1
        "https://www.forexfactory.com/ffcal_week_this.csv"            # tentative 2
    ]

    for url in urls:
        try:
            print(f"⬇️ Tentative de téléchargement : {url}")
            response = requests.get(url, timeout=15)
            if response.status_code == 200 and "Event" in response.text:
                print(f"✅ CSV téléchargé avec succès depuis {url}")
                return response.text
            else:
                print(f"⚠️ Erreur {response.status_code} ou contenu invalide sur {url}")
        except Exception as e:
            print(f"⚠️ Échec avec {url} :", e)

    raise Exception("❌ Impossible de télécharger le CSV depuis toutes les sources.")

def upload_to_google_sheets(csv_text):
    """Transforme le CSV en DataFrame puis l’upload dans Google Sheets."""
    df = pd.read_csv(pd.compat.StringIO(csv_text))
    client = get_gspread_client()
    sheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)

    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("✅ Données mises à jour dans Google Sheets :", WORKSHEET_NAME)

def main():
    try:
        csv_text = download_forexfactory_csv()
        upload_to_google_sheets(csv_text)
    except Exception as e:
        print("❌ Erreur lors de l'exécution :", e)

if __name__ == "__main__":
    main()
