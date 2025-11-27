import requests
import pandas as pd
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Sources: current season and last 2 seasons for history
URLS = [
    "https://www.football-data.co.uk/mmz4281/2324/E0.csv",
    "https://www.football-data.co.uk/mmz4281/2223/E0.csv",
    "https://www.football-data.co.uk/mmz4281/2122/E0.csv",
    "https://www.football-data.co.uk/mmz4281/2425/E0.csv"]

def fetch_data():
    dfs = []
    for url in URLS:
        try:
            filename = url.split("/")[-2] + "_" + url.split("/")[-1]
            path = os.path.join(DATA_DIR, filename)
            
            # Always download fresh
            response = requests.get(url)
            if response.status_code == 200:
                with open(path, "wb") as f:
                    f.write(response.content)
            
            if os.path.exists(path):
                df = pd.read_csv(path, encoding="unicode_escape")
                # Basic cleanup
                df = df.dropna(subset=['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
                dfs.append(df)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    
    if not dfs:
        return pd.DataFrame()
    
    full_df = pd.concat(dfs, ignore_index=True)
    
    # Standardize Date
    full_df['Date'] = pd.to_datetime(full_df['Date'], dayfirst=True, errors='coerce')
    full_df = full_df.sort_values('Date').reset_index(drop=True)
    
    return full_df
