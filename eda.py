import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

#connect to the database
conn = sqlite3.connect("crypto.db")
crypto = pd.read_sql("SELECT * FROM coin_data", conn)
conn.close()

# line chart for crypto prices over time
for coin in crypto['coin'].unique():
    coin_data = crypto[crypto['coin'] == coin]
    plt.plot(coin_data['date'], coin_data['close'], label=coin)
plt.title('Closing Price Over Time')
plt.xlabel('Date')
plt.ylabel('Closing Price (USD)')
plt.legend()
plt.grid()
plt.show()

# daily Trading Volume over time
plt.figure(figsize=(12, 6))
sns.barplot(x='date', y='volume', hue='coin', data=crypto)
plt.title('Daily Trading Volume by Cryptocurrency')
plt.xlabel('Date')
plt.ylabel('Volume (USD)')
plt.xticks(rotation=45)
plt.legend()
plt.show()

# btc candlestick plots price over time
btc_data = crypto[crypto['coin'] == 'BTC']
fig = go.Figure(data=[go.Candlestick(
    x=btc_data['date'],
    open=btc_data['open'],
    high=btc_data['high'],
    low=btc_data['low'],
    close=btc_data['close']
)])
fig.update_layout(
    title='Bitcoin OHLC Candlestick Chart',
    xaxis_title='Date',
    yaxis_title='Price (USD)',
    xaxis_rangeslider_visible=False
)
fig.show()

# closing price vs trading vol
plt.figure(figsize=(12, 6))
sns.scatterplot(x='close', y='volume', hue='coin', data=crypto)
plt.title('Closing Price vs. Trading Volume')
plt.xlabel('Closing Price (USD)')
plt.ylabel('Volume (USD)')
plt.legend()
plt.show()

# open price vs trading vol
plt.figure(figsize=(12, 6))
sns.scatterplot(x='open', y='volume', hue='coin', data=crypto)
plt.title('Open Price vs. Trading Volume')
plt.xlabel('Closing Price (USD)')
plt.ylabel('Volume (USD)')
plt.legend()
plt.show()

# open price vs market cap
plt.figure(figsize=(12, 6))
sns.scatterplot(x='open', y='market_cap', hue='coin', data=crypto)
plt.title('Open Price vs. Market Cap')
plt.xlabel('Closing Price (USD)')
plt.ylabel('Volume (USD)')
plt.legend()
plt.show()

# correlation matrix
corr_matrix = crypto[['open', 'high', 'low', 'close', 'volume', 'market_cap']].corr()

# heatmap
plt.figure(figsize=(10, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Correlation Matrix')
plt.show()

# pair plot
sns.pairplot(crypto[['open', 'high', 'low', 'close', 'volume', 'coin']], hue='coin')
plt.suptitle('Pair Plot of Cryptocurrency Data', y=1.02)
plt.show()