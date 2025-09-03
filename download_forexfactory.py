# download_forexfactory.py

import os
import json
import requests
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from io import StringIO
from datetime import datetime

SPREADSHEET_NAME = "forex"       # 👈 Ton Google Spreadsheet
WORKSHEET_NAME = "forex"         # 👈 Ton onglet

# ============================
# Connexion Google Sheets
# ============================
def get_gspread_client():
    creds_env = os.getenv("GOOGLE_CREDS")
    if not creds_env:
        raise FileNotFoundError("❌ Variable GOOGLE_CREDS introuvable dans Render.")

    try:
        creds_dict = json.loads(creds_env)
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ GOOGLE_CREDS n'est pas un JSON valide: {e}")

    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    print("✅ Connexion Google Sheets réussie via GOOGLE_CREDS")
    return client


# ============================
# Télécharger le CSV de Forex Factory
# ============================
def download_forexfactory_csv():
    url = "https://cdn-nfs.fxfactory.com/ff_calendar_thisweek.csv"  # CSV hebdo officiel
    print(f"⬇️ Téléchargement du CSV depuis {url} ...")
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"❌ Erreur téléchargement CSV : {response.status_code}")
    print("✅ CSV téléchargé avec succès")
    return response.text


# ============================
# Importer dans Google Sheets
# ============================
def import_csv_to_sheets(csv_text, client):
    sheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)
    print(f"📄 Ouverture de la feuille : {SPREADSHEET_NAME}/{WORKSHEET_NAME}")

    # Nettoyer la feuille avant d'importer
    sheet.clear()
    print("🧹 Feuille nettoyée")

    # Lire le CSV et pousser ligne par ligne
    f = StringIO(csv_text)
    reader = csv.reader(f)

    rows = list(reader)
    sheet.update("A1", rows)  # upload direct
    print(f"✅ {len(rows)} lignes importées dans Google Sheets")


# ============================
# Main
# ============================
def main():
    print("🚀 Script démarré :", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        client = get_gspread_client()
        csv_text = download_forexfactory_csv()
        import_csv_to_sheets(csv_text, client)
        print("🎯 Mise à jour terminée avec succès")
    except Exception as e:
        print("❌ Erreur lors de l'exécution :", e)


if __name__ == "__main__":
    main()
