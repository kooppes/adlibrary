import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import tempfile

def get_chromedriver():
    # Adjust path if needed
    return Service('/usr/bin/chromedriver')

def get_chrome_options():
    options = Options()
    options.binary_location = '/usr/bin/chromium-browser'  # or path to Chrome
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return options

def scrape_ads(search_term, country='United States'):
    service = get_chromedriver()
    options = get_chrome_options()
    driver = webdriver.Chrome(service=service, options=options)

    ads_data = []
    try:
        driver.get("https://www.facebook.com/ads/library")
        time.sleep(5)

        # Accept cookies if prompted
        try:
            cookie_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Allow all cookies")]')
            cookie_btn.click()
            time.sleep(2)
        except:
            pass

        # Set country
        country_input = driver.find_element(By.XPATH, '//label[contains(text(), "Country")]/following-sibling::div//input')
        country_input.clear()
        country_input.send_keys(country)
        time.sleep(1)
        country_input.send_keys(Keys.RETURN)

        # Search term
        search_input = driver.find_element(By.XPATH, '//input[@placeholder="Search ads"]')
        search_input.clear()
        search_input.send_keys(search_term)
        search_input.send_keys(Keys.RETURN)

        time.sleep(10)

        # Scroll to load more ads
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        ads = driver.find_elements(By.XPATH, '//div[contains(@data-testid, "ad")]')
        for ad in ads:
            try:
                page_name = ad.find_element(By.XPATH, './/span[contains(@class,"_9cd2")]').text
            except:
                page_name = "N/A"
            try:
                ad_text = ad.find_element(By.XPATH, './/div[contains(@data-testid,"ad_creative_body")]').text
            except:
                ad_text = "N/A"
            try:
                ad_link = ad.find_element(By.XPATH, './/a[contains(text(),"See ad details")]').get_attribute("href")
            except:
                ad_link = "N/A"

            ads_data.append({
                'Page Name': page_name,
                'Ad Text': ad_text,
                'Ad Details Link': ad_link
            })

    finally:
        driver.quit()

    return ads_data

# Streamlit UI
st.title("Meta Ad Library Scraper - Guild of Guardians Example")

search_term = st.text_input("Enter search term:", "Guild of Guardians")

if st.button("Scrape Ads"):
    with st.spinner("Scraping ads from Meta Ad Library... this may take a moment"):
        data = scrape_ads(search_term)
        if data:
            df = pd.DataFrame(data)
            st.success(f"Found {len(data)} ads!")
            st.dataframe(df)

            # CSV download
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
            df.to_csv(tmp_file.name, index=False)
            st.download_button(
                label="Download CSV",
                data=open(tmp_file.name, "rb").read(),
                file_name=f"{search_term.replace(' ', '_')}_ads.csv",
                mime="text/csv"
            )
        else:
            st.warning("No ads found or scraping failed.")

