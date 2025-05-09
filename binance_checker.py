# binance_checker.py
import requests

BINANCE_EXCHANGE_INFO_URL = "https://api.binance.com/api/v3/exchangeInfo"

def get_binance_listed_symbols():
    """Fetches all listed base asset symbols from Binance."""
    binance_symbols = set()
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(BINANCE_EXCHANGE_INFO_URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        for symbol_info in data.get('symbols', []):
            binance_symbols.add(symbol_info['baseAsset'])
    except requests.exceptions.Timeout:
        print(f"Error fetching data from Binance API: Request timed out.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Binance API: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in get_binance_listed_symbols: {e}")
    return binance_symbols

if __name__ == '__main__':
    # Test the function
    symbols = get_binance_listed_symbols()
    if symbols:
        print(f"Found {len(symbols)} base asset symbols on Binance.")
        # Example check for common symbols
        for common_sym in ['BTC', 'ETH', 'BNB']:
            print(f"Is {common_sym} in Binance symbols? {'Yes' if common_sym in symbols else 'No'}")
    else:
        print("No symbols fetched from Binance or an error occurred.")