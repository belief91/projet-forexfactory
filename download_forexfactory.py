# download_forexfactory.py

import os
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread

CREDENTIALS_FILE = "credentials.json"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def ensure_credentials():
    """
    Vérifie si credentials.json existe.
    Sinon, essaie de le créer depuis la variable d'environnement GOOGLE_CREDS.
    """
    print("🔍 Vérification des credentials...")

    # Vérifie dans le dossier courant
    if os.path.exists(CREDENTIALS_FILE):
        print(f"✅ Fichier {CREDENTIALS_FILE} trouvé.")
        return CREDENTIALS_FILE

    # Sinon, essaie depuis la variable Render
    creds_env = os.environ.get("GOOGLE_CREDS")
    if creds_env:
        print("📦 Variable d'environnement GOOGLE_CREDS trouvée, création du fichier credentials.json...")
        with open(CREDENTIALS_FILE, "w") as f:
            f.write(creds_env)
        print(f"✅ Fichier {CREDENTIALS_FILE} créé avec succès.")
        return CREDENTIALS_FILE

    # Si rien trouvé
    raise FileNotFoundError("❌ Impossible de trouver credentials.json ni la variable GOOGLE_CREDS.")

def main():
    try:
        creds_path = ensure_credentials()
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, SCOPE)
        client = gspread.authorize(creds)
        print("✅ Connexion Google Sheets réussie !")

        # Exemple : ouvrir une feuille (remplace par le vrai nom)
        sheet = client.open("Calendrier Économique Forex").sheet1
        print("📊 Nom de la première feuille :", sheet.title)

    except Exception as e:
        print("⚠️ Erreur :", e)
        raise

if __name__ == "__main__":
    main()
