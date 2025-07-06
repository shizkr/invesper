import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Fetch historical data for gold price
symbol = "GC=F"  # Gold Futures symbol on Yahoo Finance
gold_data = yf.download(symbol, start="1975-01-01", end=datetime.datetime.now().strftime("%Y-%m-%d"))

# Reset index for easier handling
gold_data.reset_index(inplace=True)

# Plotting the gold price
plt.figure(figsize=(12, 6))
plt.plot(gold_data['Date'], gold_data['Close'], label='Gold Price')
plt.title('Gold Price')
plt.xlabel('Date')
plt.ylabel('Price (USD per ounce)')
plt.grid(True)
plt.legend()

# Highlighting the latest value
last_date = pd.Timestamp(gold_data['Date'].iloc[-1])  # Ensure proper date formatting
last_price = float(gold_data['Close'].iloc[-1])  # Ensure scalar float value for formatting
plt.scatter(last_date, last_price, color='red', zorder=5)
plt.text(
    last_date, last_price,
    f"${last_price:.2f}\n{last_date.strftime('%Y-%m-%d')}",
    fontsize=10, color='red', va='bottom', ha='right',
    bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.3')
)

plt.tight_layout()
plt.show()
