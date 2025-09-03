# download_forexfactory_scraping.py

import os
import json
import requests
import gspread
import pandas as pd
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials

# === CONFIG ===
SPREADSHEET_NAME = "forex"
WORKSHEET_NAME = "forex"
CALENDAR_URL = "https://www.forexfactory.com/calendar?week=this"

# Connexion Google Sheets
def get_gspread_client():
    creds_env = os.getenv("GOOGLE_CREDS")
    if not creds_env:
        raise FileNotFoundError("❌ Variable GOOGLE_CREDS introuvable dans Render.")

    creds_dict = json.loads(creds_env)
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    print("✅ Connexion Google Sheets réussie")
    return client

# Scraper ForexFactory
def scrape_forexfactory():
    print(f"🌍 Téléchargement de {CALENDAR_URL} ...")
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(CALENDAR_URL, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.select("table.calendar__table tbody tr")

    data = []
    for row in rows:
        # Récupération colonnes du tableau
        time = row.select_one(".calendar__time")
        currency = row.select_one(".calendar__currency")
        impact = row.select_one(".impact span")
        event = row.select_one(".calendar__event")
        actual = row.select_one(".calendar__actual")
        forecast = row.select_one(".calendar__forecast")
        previous = row.select_one(".calendar__previous")

        if event:
            data.append({
                "Time": time.get_text(strip=True) if time else "",
                "Currency": currency.get_text(strip=True) if currency else "",
                "Impact": impact.get("title") if impact else "",
                "Event": event.get_text(strip=True),
                "Actual": actual.get_text(strip=True) if actual else "",
                "Forecast": forecast.get_text(strip=True) if forecast else "",
                "Previous": previous.get_text(strip=True) if previous else ""
            })

    print(f"✅ {len(data)} événements extraits")
    return pd.DataFrame(data)

# Envoi vers Google Sheets
def upload_to_sheets(df, client):
    sheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("📤 Données mises à jour dans Google Sheets")

def main():
    try:
        client = get_gspread_client()
        df = scrape_forexfactory()
        if not df.empty:
            upload_to_sheets(df, client)
        else:
            print("⚠️ Aucun événement trouvé")
    except Exception as e:
        print("❌ Erreur :", e)

if __name__ == "__main__":
    main()
