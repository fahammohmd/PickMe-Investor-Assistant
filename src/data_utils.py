import pandas as pd
import streamlit as st
import os
import glob

# This file centralizes all data loading logic for stock prices.

@st.cache_data
def load_stock_data(filepath, is_pickme=False):
    """Loads and processes a single stock price history CSV."""
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        st.error(f"Error: The file '{filepath}' was not found.")
        return None

    # Clean column names based on file type
    if is_pickme:
        df.columns = [
            'date', 'open', 'high', 'low', 'close', 
            'trade_volume', 'share_volume', 'turnover'
        ]
    else:
        df.columns = [col.strip().lower().replace(' (rs.)', '').replace(' ', '_') for col in df.columns]

    df = df.rename(columns={'trade_date': 'date'})
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').set_index('date')
    
    # Remove duplicate dates, keeping the last entry
    df = df[~df.index.duplicated(keep='last')]
    
    # Calculate basic indicators
    df['ma_20'] = df['close'].rolling(window=20).mean()
    df['ma_50'] = df['close'].rolling(window=50).mean()
    df['returns'] = df['close'].pct_change()
    
    return df

@st.cache_data
def load_all_stock_data():
    """Loads all stock data from the root CSV and the stock-prices folder."""
    all_files = glob.glob("stock-prices/*.csv")
    
    all_dfs = {}

    # Load other stocks
    for file in all_files:
        try:
            df = pd.read_csv(file)
            df.columns = [col.strip().lower().replace(' (rs.)', '').replace(' ', '_') for col in df.columns]
            df = df.rename(columns={'trade_date': 'date'})
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').set_index('date')
            df = df[~df.index.duplicated(keep='last')]
            
            ticker = os.path.basename(file).replace('.csv', '')
            all_dfs[ticker] = df['close']
        except Exception:
            continue
            
    # Load PKME separately to ensure it's included
    try:
        pickme_df = pd.read_csv("PKME_Stock_Price_History.csv")
        pickme_df.columns = ['date', 'open', 'high', 'low', 'close', 'trade_volume', 'share_volume', 'turnover']
        pickme_df['date'] = pd.to_datetime(pickme_df['date'])
        pickme_df = pickme_df.sort_values('date').set_index('date')
        pickme_df = pickme_df[~pickme_df.index.duplicated(keep='last')]
        all_dfs['PKME'] = pickme_df['close']
    except Exception:
        st.error("Could not load PKME_Stock_Price_History.csv")

    if not all_dfs:
        return None
    
    combined_df = pd.concat(all_dfs, axis=1).sort_index()
    return combined_df.dropna()
