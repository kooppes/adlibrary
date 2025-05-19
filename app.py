import streamlit as st
import requests
import pandas as pd

st.title("🔍 Meta Ad Library Scraper")

# User inputs
access_token = st.text_input("🔑 Enter your Meta Access Token", type="password")
search_term = st.text_input("📌 Search Keyword (e.g., Biden, Environment)")
country = st.text_input("🌍 Country Code (e.g., US, FR)", value="US")
limit = st.slider("Number of Ads to Retrieve", min_value=1, max_value=100, value=25)

if st.button("Search Ads"):
    if not access_token or not search_term or not country:
        st.error("Please fill in all fields.")
    else:
        st.info("Fetching ads from Meta Ad Library API...")
        url = "https://graph.facebook.com/v19.0/ads_archive"
        params = {
            "search_terms": search_term,
            "ad_reached_countries": country,
            "ad_type": "POLITICAL_AND_ISSUE_ADS",
            "fields": "ad_creative_body,ad_creative_link_caption,ad_creative_link_title,ad_delivery_start_time,ad_delivery_stop_time,page_name",
            "limit": limit,
            "access_token": access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            ads = data.get("data", [])
            
            if len(ads) == 0:
                st.warning("No ads found for your query.")
            else:
                # Convert to DataFrame
                df = pd.DataFrame(ads)
                st.success(f"Found {len(df)} ads.")
                st.dataframe(df)
                
                # Download CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download CSV", csv, "meta_ads.csv", "text/csv")
        
        except requests.exceptions.HTTPError as errh:
            st.error(f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            st.error(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            st.error(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            st.error(f"Oops! Something went wrong: {err}")
