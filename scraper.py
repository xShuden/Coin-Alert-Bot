# scraper.py
import requests
from bs4 import BeautifulSoup
import re

LISTEDON_URL = "https://listedon.org/en/search?page=1&exchange=&text=&sort=date&order=0"

def fetch_new_listings_from_listedon():
    """Fetches new crypto listings from listedon.org and extracts tickers."""
    tickers = set() # Use a set to store unique tickers
    try:
        # Using a common user-agent header can sometimes help avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(LISTEDON_URL, headers=headers, timeout=15) # Increased timeout
        response.raise_for_status() # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # This regex targets [TICKER](https://listedon.org/en/ticker/TICKER)
        # It looks for 2 or more uppercase letters/digits for the ticker.
        ticker_regex = r'\[([A-Z0-9]{2,})\]\(https://listedon\.org/en/ticker/[A-Z0-9]{2,}\)'
        
        matches = re.findall(ticker_regex, str(soup))
        for match in matches:
            # The regex re.findall with one capturing group returns a list of strings (the captured groups)
            tickers.add(match) 
    
    except requests.exceptions.Timeout:
        print(f"Error fetching data from listedon.org: Request timed out after 15 seconds.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from listedon.org: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in fetch_new_listings_from_listedon: {e}")
    return list(tickers)

if __name__ == '__main__':
    # Test the function
    latest_tickers = fetch_new_listings_from_listedon()
    if latest_tickers:
        print(f"Fetched {len(latest_tickers)} tickers from listedon.org: {latest_tickers[:10]}...") # Print first 10
    else:
        print("No tickers fetched from listedon.org or an error occurred.")