import pandas as pd
import sqlite3
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import os
from git import Repo
from datetime import datetime

def fetch_and_generate_charts():
    # connect to the database
    conn = sqlite3.connect("crypto.db")
    crypto = pd.read_sql("SELECT * FROM coin_data", conn)
    conn.close()

    # independent and dependent variables
    ind = ['open', 'high', 'low', 'volume', 'market_cap']
    dep = 'close'

    # drop rows with missing values
    crypto_clean = crypto.dropna()

    # define x and y
    X = crypto_clean[ind]
    y = crypto_clean[dep]

    # split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # define and train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # predict closing price for next day
    crypto_clean['predicted_close'] = model.predict(crypto_clean[['open', 'high', 'low', 'volume', 'market_cap']])

    # generate buy signals
    threshold = 0.01
    crypto_clean['buy_signal'] = crypto_clean['predicted_close'] > (1 + threshold) * crypto_clean['close']

    # function to generate interactive charts
    def generate_interactive_chart(coin_data, coin_name):
        buy_signals = coin_data[coin_data['buy_signal']]
        
        fig = go.Figure()

        # add closing price line
        fig.add_trace(go.Scatter(
            x=coin_data['date'],
            y=coin_data['close'],
            mode='lines',
            name='closing price',
            line=dict(color='blue')
        ))

        # add buy signals
        fig.add_trace(go.Scatter(
            x=buy_signals['date'],
            y=buy_signals['close'],
            mode='markers',
            name='buy signal',
            marker=dict(color='green', symbol='triangle-up', size=10)
        ))

        # update layout
        fig.update_layout(
            title=f'{coin_name} price chart with 4-day model-based buy signals',
            xaxis_title='date',
            yaxis_title='price (usd)',
            hovermode='x unified'
        )

        # save the chart as an html file
        fig.write_html(f'{coin_name.lower()}_buy_signals.html')

    # generate charts for btc and eth
    btc_data = crypto_clean[crypto_clean['coin'] == 'BTC']
    generate_interactive_chart(btc_data, 'bitcoin')

    eth_data = crypto_clean[crypto_clean['coin'] == 'ETH']
    generate_interactive_chart(eth_data, 'ethereum')

    # push changes to github
    repo = Repo(os.getcwd())
    repo.git.add('bitcoin_buy_signals.html')
    repo.git.add('ethereum_buy_signals.html')
    repo.git.commit('-m', f'update charts with new data - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    repo.git.push()

# run the function to fetch data and generate charts
fetch_and_generate_charts()
