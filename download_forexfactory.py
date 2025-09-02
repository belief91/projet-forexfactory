# download_forexfactory.py

import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_gspread_client():
    """
    Charge les credentials depuis la variable d'environnement GOOGLE_CREDS
    et initialise le client Google Sheets.
    """
    creds_env = os.getenv("GOOGLE_CREDS")
    if not creds_env:
        raise FileNotFoundError("❌ Variable GOOGLE_CREDS introuvable dans Render.")

    try:
        creds_dict = json.loads(creds_env)  # transforme le JSON en dict
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ GOOGLE_CREDS n'est pas un JSON valide: {e}")

    # Initialiser le client
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    print("✅ Connexion Google Sheets réussie via GOOGLE_CREDS")
    return client

def main():
    try:
        client = get_gspread_client()
        # test simple : ouvrir ta feuille
        sheet = client.open("Calendrier Économique Forex").worksheet("Calendrier Économique Forex")
        print("✅ Feuille trouvée :", sheet.title)
    except Exception as e:
        print("❌ Erreur :", e)

if __name__ == "__main__":
    main()
