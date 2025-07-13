import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 1. Fetch Bitcoin daily price data for last ~1 years (max allowed by CoinGecko is 365 days)
url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
params = {
    "vs_currency": "usd",
    "days": "365",  # 1 years
    "interval": "daily"
}
resp = requests.get(url, params=params)
data = resp.json()

# 2. Parse data to DataFrame
prices = data["prices"]  # Each item: [timestamp(ms), price]
df = pd.DataFrame(prices, columns=['timestamp', 'price'])
df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('date', inplace=True)

# 3. Plot chart
plt.figure(figsize=(16,8))
plt.plot(df.index, df['price'], label='BTC Price (USD)')
plt.title('Bitcoin Price - Last 1 Years')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.grid(True)

# 4. Annotate last price and date
last_date = df.index[-1]
last_price = df['price'].iloc[-1]
plt.scatter(last_date, last_price, color='red', zorder=5)
plt.annotate(
    f'{last_date.strftime("%Y-%m-%d")}\n${last_price:,.2f}',
    xy=(last_date, last_price),
    xytext=(-80,30),
    textcoords='offset points',
    arrowprops=dict(arrowstyle="->", color='red'),
    fontsize=12,
    backgroundcolor='white',
    color='red'
)

plt.legend()
plt.tight_layout()
plt.show()
