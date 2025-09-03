import time
import random
import datetime
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

# =========================
# Config
# =========================
CREDENTIALS_FILE = "credentials.json"
SPREADSHEET_ID = "1ayYyGCF6RLaiizDqLRdU7EN7rwhQDbkMzG3IssMJgBM"   # ⚠️ Mets ton vrai ID ici
WORKSHEET_NAME = "forex"  # Onglet Google Sheets

FOREXFACTORY_URL = "https://www.forexfactory.com/calendar?week={}"

# =========================
# Scraping
# =========================
def scrape_forex_factory(week):
    url = FOREXFACTORY_URL.format(week)
    print(f"🌐 Scraping URL : {url}")

    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    driver = uc.Chrome(options=options)

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.calendar__row")))

        rows = driver.find_elements(By.CSS_SELECTOR, "tr.calendar__row")

        events = []
        current_date = None

        for row in rows:
            try:
                # Vérifier la date
                date_cell = row.find_element(By.CSS_SELECTOR, "td.calendar__date").text.strip()
                if date_cell:
                    current_date = date_cell
                if not current_date:
                    continue

                impact = row.find_element(By.CSS_SELECTOR, "td.calendar__impact span").get_attribute("title")

                # Mapper impact → nombre de taureaux
                impact_map = {
                    "Low Impact Expected": "1 tête",
                    "Medium Impact Expected": "2 têtes",
                    "High Impact Expected": "3 têtes"
                }
                impact_label = impact_map.get(impact, impact)

                if "Impact" not in impact:
                    continue  # éviter les lignes vides

                time_cell = row.find_element(By.CSS_SELECTOR, "td.calendar__time").text.strip()
                currency = row.find_element(By.CSS_SELECTOR, "td.calendar__currency").text.strip()
                event = row.find_element(By.CSS_SELECTOR, "td.calendar__event").text.strip()
                forecast = row.find_element(By.CSS_SELECTOR, "td.calendar__forecast").text.strip()
                previous = row.find_element(By.CSS_SELECTOR, "td.calendar__previous").text.strip()
                actual = row.find_element(By.CSS_SELECTOR, "td.calendar__actual").text.strip()

                events.append({
                    "Date": current_date,
                    "Heure": time_cell,
                    "Devise": currency,
                    "Événement": event,
                    "Impact": impact_label,
                    "Prévision": forecast,
                    "Précédent": previous,
                    "Réel": actual
                })
            except Exception:
                continue

        df = pd.DataFrame(events)
        print(f"✅ {len(df)} événements récupérés ({week})")
        return df

    except Exception as e:
        print(f"❌ Erreur scraping : {e}")
        return pd.DataFrame()

    finally:
        driver.quit()

# =========================
# Google Sheets
# =========================
def update_google_sheets(df):
    if df.empty:
        print("⚠️ Aucun événement à envoyer dans Google Sheets.")
        return
    try:
        print("📡 Connexion à Google Sheets…")
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        ws = client.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET_NAME)
        ws.clear()
        ws.update([df.columns.tolist()] + df.values.tolist())
        print("✅ Données mises à jour avec succès !")
    except Exception as e:
        print(f"❌ Erreur Google Sheets : {e}")

# =========================
# Vérification semaine courante/next
# =========================
def get_next_week_if_needed(df, current_week):
    if df.empty:
        print("⚠️ Aucun événement trouvé cette semaine, on passe à la suivante.")
        return current_week + datetime.timedelta(weeks=1)

    try:
        last_event_date = df["Date"].dropna().iloc[-1]
        print(f"📅 Dernier événement trouvé : {last_event_date}")
        today = datetime.date.today().strftime("%b %d")
        if today > last_event_date:
            print("➡️ La semaine est terminée, on scrape la suivante.")
            return current_week + datetime.timedelta(weeks=1)
        else:
            print("✅ La semaine en cours contient encore des événements.")
            return current_week
    except Exception as e:
        print(f"⚠️ Erreur lors de la vérification de la semaine : {e}")
        return current_week

# =========================
# Main
# =========================
def main():
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())  # lundi de la semaine
    current_week = monday

    df = scrape_forex_factory(current_week)
    week_to_scrape = get_next_week_if_needed(df, current_week)

    if week_to_scrape != current_week:
        time.sleep(random.randint(20, 40))  # pause pour éviter blocage
        df = scrape_forex_factory(week_to_scrape)

    update_google_sheets(df)

if __name__ == "__main__":
    main()
