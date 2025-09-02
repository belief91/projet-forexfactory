# download_forexfactory.py

import os
import pandas as pd
import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# ----------------- DEBUG Render -----------------
print("📂 Contenu du dossier courant :", os.listdir("."))
print("📂 Contenu du dossier / :", os.listdir("/"))
print("📂 Contenu du dossier /opt/render/project/src :", os.listdir("/opt/render/project/src"))
print("✅ credentials.json existe ?", os.path.exists("credentials.json"))
# ------------------------------------------------

# ⚠️ Mets bien le bon chemin vers ton credentials.json
CREDENTIALS_FILE = "credentials.json"

# Vérification supplémentaire
if not os.path.exists(CREDENTIALS_FILE):
    raise FileNotFoundError(f"❌ Fichier {CREDENTIALS_FILE} introuvable ! Vérifie sur Render.")

# Connexion à Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)

# Identifiant Google Sheet
SHEET_NAME = "Calendrier Économique Forex"
WORKSHEET_NAME = "Calendrier Économique Forex"

# Accès à la feuille
sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

# ----------------- Exemple simple -----------------
# Ici on va simuler un téléchargement CSV ForexFactory
# Tu peux remplacer par ton vrai scraping ou téléchargement
url = "https://cdn-nfs.faireconomy.media/ff_calendar_thisweek.csv"
response = requests.get(url)

if response.status_code == 200:
    with open("forexfactory.csv", "wb") as f:
        f.write(response.content)
    print("✅ Fichier CSV téléchargé avec succès.")

    # Charger le CSV en DataFrame
    df = pd.read_csv("forexfactory.csv")

    # (Optionnel) Afficher un aperçu
    print(df.head())

    # Écrire dans Google Sheets (écrase tout)
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("✅ Google Sheets mis à jour avec succès.")

else:
    print(f"❌ Erreur téléchargement CSV ForexFactory : {response.status_code}")
