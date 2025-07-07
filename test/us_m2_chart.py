import pandas_datareader.data as web
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Get last 10 years
end = datetime.today()
start = end - timedelta(days=365*10)

# Download US M2 Money Stock from FRED ("M2SL")
df = web.DataReader('M2SL', 'fred', start, end)

plt.figure(figsize=(14, 7))
plt.plot(df.index, df['M2SL'], label='US M2 Money Stock')
plt.title('US M2 Money Stock (Last 10 Years)')
plt.xlabel('Date')
plt.ylabel('Billions of Dollars')
plt.legend()
plt.grid()

# Annotate last value and date
last_date = df.index[-1].strftime('%Y-%m-%d')
last_value = df['M2SL'][-1]
plt.annotate(f"{last_value:.2f} ({last_date})",
             xy=(df.index[-1], last_value),
             xytext=(-100, 40),
             textcoords='offset points',
             arrowprops=dict(arrowstyle='->', color='red'),
             fontsize=12,
             color='red',
             bbox=dict(boxstyle="round,pad=0.3", edgecolor='red', facecolor='white', alpha=0.8))

plt.show()
