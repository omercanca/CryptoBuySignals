import requests
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

def get_coin_info(coin_id, coin_ticker):
    days = 180  # declaring days for the API date range
    OHLC = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
    ResponseOHLC = requests.get(OHLC)
    DataOHLC = ResponseOHLC.json()
    
    # printing head for error checking
    print(f"[DEBUG] {coin_ticker} OHLC raw data:", DataOHLC[:2]) 
    
    # if the endpoint doesn't work, use the API's market chart to get the info
    if not DataOHLC:
        UrlMarket = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
        ResponseMarket = requests.get(UrlMarket)
        MarketChart = ResponseMarket.json()
        
        # printing pricing data
        print(f"[DEBUG] {coin_ticker} fallback - prices raw data:", MarketChart.get("prices", [])[:2])
        CryptoPrices = pd.DataFrame(MarketChart.get("prices", []), columns=["timestamp", "price"])
        CryptoPrices["date"] = pd.to_datetime(CryptoPrices["timestamp"], unit="ms").dt.date
        OHLCdf = CryptoPrices.groupby("date", as_index=False).agg(
            open=("price", "first"),
            high=("price", "max"),
            low=("price", "min"),
            close=("price", "last")
        )
    else:
        # if OHLC data is available, create the OHLC DataFrame
        OHLCdf = pd.DataFrame(DataOHLC, columns=["timestamp", "open", "high", "low", "close"])
        OHLCdf["date"] = pd.to_datetime(OHLCdf["timestamp"], unit="ms").dt.date
        
        # use Market Chart for volume and market cap
        UrlMarket = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
        ResponseMarket = requests.get(UrlMarket)
        MarketChart = ResponseMarket.json()
    
    # make sure data market is working (ERROR CHECK)
    if 'MarketChart' not in locals():
        UrlMarket = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
        ResponseMarket = requests.get(UrlMarket)
        MarketChart = ResponseMarket.json()
    
    # Debug print for market_chart data keys
    print(f"[DEBUG] {coin_ticker} market_chart keys:", list(MarketChart.keys()))
    
    # if volume data is in marketchart, put it in the df, else print nothing
    if "total_volumes" in MarketChart and MarketChart["total_volumes"]:
        volumes_df = pd.DataFrame(MarketChart["total_volumes"], columns=["timestamp", "volume"])
        volumes_df["date"] = pd.to_datetime(volumes_df["timestamp"], unit="ms").dt.date
    else:
        volumes_df = pd.DataFrame(columns=["timestamp", "volume", "date"])
    volume_daily = volumes_df.groupby("date", as_index=False).agg({"volume": "last"})
    print(f"[DEBUG] {coin_ticker} volume_daily:", volume_daily.head(2))
    
    # do the same thing for market cap
    if "market_caps" in MarketChart and MarketChart["market_caps"]:
        market_caps_df = pd.DataFrame(MarketChart["market_caps"], columns=["timestamp", "market_cap"])
        market_caps_df["date"] = pd.to_datetime(market_caps_df["timestamp"], unit="ms").dt.date
    else:
        market_caps_df = pd.DataFrame(columns=["timestamp", "market_cap", "date"])
    market_cap_daily = market_caps_df.groupby("date", as_index=False).agg({"market_cap": "last"})
    print(f"[DEBUG] {coin_ticker} market_cap_daily:", market_cap_daily.head(2))
    
    # merge the 3 tables together
    merged_data = pd.merge(OHLCdf[["date", "open", "high", "low", "close"]],
                           volume_daily, on="date", how="left")
    merged_data = pd.merge(merged_data, market_cap_daily, on="date", how="left")
    
    # add column for coin and merge the dataframe
    merged_data["coin"] = coin_ticker
    final_df = merged_data[["coin", "date", "open", "high", "low", "close", "volume", "market_cap"]]
    return final_df

# define the coins we are using, btc, eth, and xrp
coins = [
    {"id": "bitcoin", "ticker": "BTC"},
    {"id": "ethereum", "ticker": "ETH"},
]

# name our df
all_coin_data = pd.DataFrame()

# for every coin, get its info and concat
for coin in coins:
    coin_data = get_coin_info(coin["id"], coin["ticker"])
    all_coin_data = pd.concat([all_coin_data, coin_data], ignore_index=True)

# put in sqlite database
conn = sqlite3.connect("crypto.db")
all_coin_data.to_sql("coin_data", conn, if_exists="replace", index=False)
conn.close()