import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager


# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------

HEADLESS_MODE = False          # True = hidden browser
OUTPUT_FILE = "imdb_top250.csv"

IMDB_URL = "https://www.imdb.com/chart/top/"


# -------------------------------------------------
# CREATE CHROME DRIVER
# -------------------------------------------------

def get_driver():

    options = Options()

    if HEADLESS_MODE:
        options.add_argument("--headless=new")

    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    )

    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(
        service=service,
        options=options
    )

    return driver


# -------------------------------------------------
# SCRAPE IMDb TOP 250
# -------------------------------------------------

def scrape_imdb():

    driver = get_driver()

    movies = []

    try:

        print("\nOpening IMDb Website...\n")

        driver.get(IMDB_URL)

        # Wait until movies appear
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")
            )
        )

        time.sleep(3)

        # Scroll down fully
        print("Scrolling page...\n")

        last_height = driver.execute_script(
            "return document.body.scrollHeight"
        )

        while True:

            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            time.sleep(2)

            new_height = driver.execute_script(
                "return document.body.scrollHeight"
            )

            if new_height == last_height:
                break

            last_height = new_height

        # Find all movie rows
        rows = driver.find_elements(
            By.CSS_SELECTOR,
            "li.ipc-metadata-list-summary-item"
        )

        print(f"Found {len(rows)} Movies\n")

        # Extract movie details
        for index, row in enumerate(rows, start=1):

            try:

                # Movie title
                title_text = row.find_element(
                    By.CSS_SELECTOR,
                    "h3.ipc-title__text"
                ).text.strip()

                # Remove ranking number
                if ". " in title_text:
                    rank, title = title_text.split(". ", 1)
                else:
                    rank = index
                    title = title_text

                # Metadata
                meta = row.find_elements(
                    By.CSS_SELECTOR,
                    "span.cli-title-metadata-item"
                )

                year = meta[0].text if len(meta) > 0 else "N/A"
                runtime = meta[1].text if len(meta) > 1 else "N/A"
                certificate = meta[2].text if len(meta) > 2 else "N/A"

                # IMDb rating
                try:
                    rating = row.find_element(
                        By.CSS_SELECTOR,
                        "span.ipc-rating-star--rating"
                    ).text
                except:
                    rating = "N/A"

                # Vote count
                try:
                    votes = row.find_element(
                        By.CSS_SELECTOR,
                        "span.ipc-rating-star--voteCount"
                    ).text
                except:
                    votes = "N/A"

                movies.append({
                    "Rank": rank,
                    "Title": title,
                    "Year": year,
                    "Runtime": runtime,
                    "Certificate": certificate,
                    "IMDb Rating": rating,
                    "Votes": votes
                })

                print(f"{rank}. {title}")

            except Exception as e:
                print(f"Error in row {index}: {e}")

    except Exception as e:
        print("\nERROR:", e)

    finally:
        driver.quit()

    return pd.DataFrame(movies)


# -------------------------------------------------
# SAVE CSV FILE
# -------------------------------------------------

def save_csv(df):

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nCSV Saved Successfully -> {OUTPUT_FILE}")


# -------------------------------------------------
# MAIN PROGRAM
# -------------------------------------------------

if __name__ == "__main__":

    print("=" * 50)
    print("IMDb TOP 250 MOVIE SCRAPER")
    print("=" * 50)

    dataframe = scrape_imdb()

    if dataframe.empty:
        print("\nNo data scraped")
    else:
        print("\nTop 10 Movies:\n")
        print(dataframe.head(10))

        save_csv(dataframe)
