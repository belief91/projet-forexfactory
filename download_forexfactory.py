import os
import pandas as pd
import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# === Bloc de debug Render ===
print("=== DEBUG Render ===")
print("Chemin courant :", os.getcwd())
print("Fichiers dans le dossier courant :", os.listdir("."))
print("====================")

# Connexion Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Téléchargement du CSV ForexFactory (exemple d’URL, adapte selon ton besoin)
url = "https://cdn-nfs.faireconomy.media/ff_calendar_thisweek.csv"
r = requests.get(url)

with open("forexfactory.csv", "wb") as f:
    f.write(r.content)

print("✅ Fichier forexfactory.csv téléchargé.")

# Lecture et push dans Google Sheets
df = pd.read_csv("forexfactory.csv")

# Ton sheet (remplace par ton ID et onglet exacts)
sheet = client.open("Calendrier Économique Forex").worksheet("Calendrier Économique Forex")
sheet.update([df.columns.values.tolist()] + df.values.tolist())

print("✅ Données envoyées dans Google Sheets avec succès.")
