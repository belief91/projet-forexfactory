import requests
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# === CONFIGURATION GOOGLE SHEETS ===
SPREADSHEET_NAME = "forex"
WORKSHEET_NAME = "forex"

# === CONFIGURATION FOREX FACTORY ===
CSV_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.csv"
LOCAL_CSV = "forexfactory.csv"
TEMP_CSV = "forexfactory_new.csv"


def download_new_csv():
    """Télécharge la version actuelle du CSV"""
    response = requests.get(CSV_URL)
    if response.status_code == 200:
        with open(TEMP_CSV, "wb") as f:
            f.write(response.content)
        print("✅ Nouveau CSV téléchargé.")
    else:
        print(f"❌ Erreur téléchargement nouveau CSV : {response.status_code}")


def compare_and_update():
    """Compare l’ancien CSV et le nouveau, met à jour si différence sur 'Reel'"""
    if not os.path.exists(LOCAL_CSV):
        print("⚠️ Ancien fichier introuvable, initialisation...")
        os.rename(TEMP_CSV, LOCAL_CSV)
        return

    old_df = pd.read_csv(LOCAL_CSV)
    new_df = pd.read_csv(TEMP_CSV)

    # Comparer uniquement la colonne "Revised" ou "Actual"/"Reel"
    if "Actual" in old_df.columns:
        col = "Actual"
    elif "Revised" in old_df.columns:
        col = "Revised"
    else:
        print("❌ Pas de colonne 'Reel' trouvée.")
        return

    if old_df[col].equals(new_df[col]):
        print("ℹ️ Pas de changement détecté dans la colonne 'Reel'.")
        os.remove(TEMP_CSV)
    else:
        print("✅ Nouveaux résultats détectés → mise à jour...")
        os.replace(TEMP_CSV, LOCAL_CSV)
        upload_to_google_sheets(new_df)


def upload_to_google_sheets(df):
    """Met à jour Google Sheets"""
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)

    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("✅ Google Sheets mis à jour.")


if __name__ == "__main__":
    download_new_csv()
    compare_and_update()
