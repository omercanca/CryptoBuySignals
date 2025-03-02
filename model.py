import pandas as pd
import sqlite3
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

def fetch_and_generate_charts():
    # Connect to the database
    conn = sqlite3.connect("crypto.db")
    crypto = pd.read_sql("SELECT * FROM coin_data", conn)
    conn.close()

    # Independent and dependent variables
    ind = ['open', 'high', 'low', 'volume', 'market_cap']
    dep = 'close'

    # Drop rows with missing values
    crypto_clean = crypto.dropna()

    # Define X and y
    X = crypto_clean[ind]
    y = crypto_clean[dep]

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Define and train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Predict closing price for next day
    crypto_clean['predicted_close'] = model.predict(crypto_clean[['open', 'high', 'low', 'volume', 'market_cap']])

    # Generate buy signals
    threshold = 0.01
    crypto_clean['buy_signal'] = crypto_clean['predicted_close'] > (1 + threshold) * crypto_clean['close']

    # Function to generate interactive charts
    def generate_interactive_chart(coin_data, coin_name):
        buy_signals = coin_data[coin_data['buy_signal']]
        
        fig = go.Figure()

        # Add closing price line
        fig.add_trace(go.Scatter(
            x=coin_data['date'],
            y=coin_data['close'],
            mode='lines',
            name='Closing Price',
            line=dict(color='blue')
        ))

        # Add buy signals
        fig.add_trace(go.Scatter(
            x=buy_signals['date'],
            y=buy_signals['close'],
            mode='markers',
            name='Buy Signal',
            marker=dict(color='green', symbol='triangle-up', size=10)
        ))

        # Update layout
        fig.update_layout(
            title=f'{coin_name} Price Chart with 4-Day Model-Based Buy Signals',
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            hovermode='x unified'
        )

        # Save the chart as an HTML file
        fig.write_html(f'{coin_name.lower()}_buy_signals.html')

    # Generate charts for BTC and ETH
    btc_data = crypto_clean[crypto_clean['coin'] == 'BTC']
    generate_interactive_chart(btc_data, 'Bitcoin')

    eth_data = crypto_clean[crypto_clean['coin'] == 'ETH']
    generate_interactive_chart(eth_data, 'Ethereum')

# Run the function to fetch data and generate charts
fetch_and_generate_charts()
