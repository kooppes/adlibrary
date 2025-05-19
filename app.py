import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

st.title("Meta Ad Library Scraper (Unofficial, Selenium)")

search_term = st.text_input("Search Term (e.g. Nike, Biden)", value="")
country = st.selectbox("Country", ["US", "GB", "FR", "DE", "CA"], index=0)
max_ads = st.slider("Max ads to fetch", 1, 50, 10)

def scrape_ads(search_term, country, max_ads):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    base_url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={search_term}"
    driver.get(base_url)
    
    time.sleep(5)  # Let the page load
    
    ads_data = []
    scroll_pause_time = 2
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while len(ads_data) < max_ads:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        
        # The ads are in divs with aria-label 'Ad preview' but this can change over time
        ads = driver.find_elements(By.CSS_SELECTOR, "div[aria-label='Ad preview']")
        
        for ad in ads[len(ads_data):max_ads]:
            try:
                page_name = ad.find_element(By.CSS_SELECTOR, "strong").text
            except:
                page_name = ""
            try:
                ad_text = ad.find_element(By.CSS_SELECTOR, "div[data-testid='ad_body']").text
            except:
                ad_text = ""
            try:
                link = ad.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            except:
                link = ""
            ads_data.append({
                "Page Name": page_name,
                "Ad Text": ad_text,
                "Link": link
            })
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    driver.quit()
    return ads_data[:max_ads]

if st.button("Scrape Ads"):
    if not search_term.strip():
        st.error("Please enter a search term.")
    else:
        with st.spinner("Scraping ads from Meta Ad Library..."):
            ads = scrape_ads(search_term, country, max_ads)
            if ads:
                df = pd.DataFrame(ads)
                st.success(f"Found {len(df)} ads.")
                st.dataframe(df)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", csv, "meta_ads.csv", "text/csv")
            else:
                st.warning("No ads found or unable to scrape.")
